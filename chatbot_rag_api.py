from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocketDisconnect, WebSocket
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from typing import List, AsyncIterable
import pandas as pd
import os, json, asyncio
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.agents import Tool, initialize_agent

load_dotenv()
app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "chatbot-knowledge-base"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536, 
        metric='dotproduct',  
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )
else:
    pass
index = pc.Index(index_name)

model_name = 'text-embedding-ada-002'
embed = OpenAIEmbeddings(model=model_name, openai_api_key=OPENAI_API_KEY)
vectorstore = PineconeVectorStore(index, embed.embed_query, "text")

llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name='gpt-3.5-turbo', temperature=0.0, streaming=True)
conversational_memory = ConversationBufferWindowMemory(memory_key='chat_history', k=7, return_messages=True)
qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever())

tools = [
    Tool(
        name="Knowledge Base",
        func=qa.run,
        description="""
        'use this tool when answering general knowledge queries to get '
        'more information about the campuses, courses, modules etc'
        'provide accurate information about the courses in points'
        'summerize the response into simple and structured response'
        'only give related answers, do not go out of context'
        'DO NOT MAKE UP ANSWERS'
        """
    )
]

agent = initialize_agent(
    tools=tools, 
    llm=llm, 
    max_iterations=5, 
    memory=conversational_memory, 
    verbose=True, 
    agent="chat-conversational-react-description"
)

class Query(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {
        "message": "Chatbot API",
        "usage": "Send a POST request to the /insert_data/ endpoint with a json file to insert data into vector database and /user_query/ for query.",
        "example1": {
            "endpoint": "/insert_data/",
            "method": "POST",
            "file_type": "json",
        },
        "example2": {
            "endpoint": "/user_query/",
        }
    }

@app.post("/insert_data/")
async def insert_data(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        data = json.loads(contents)
        data_rows = [
            {
                'campus': campus['title'],
                'campus_description': campus['description'],
                'course': course['title'],
                'course_description': course['description'],
                'module': module['title'],
                'module_description': module['description']
            }
            for campus in data['content']
            for course in campus['courses']
            for module in course['modules']
        ]
        df = pd.DataFrame(data_rows)
        
        grouped_courses = df.groupby('campus')['course'].apply(lambda x: ', '.join(x)).reset_index()
        for description in range(len(df['campus_description'])):
            campus_value = df.loc[description, 'campus']
            course_list = grouped_courses[grouped_courses['campus'] == campus_value]['course'].values[0]
            df.loc[description, 'campus_description'] += '. Courses available in this campus are ' + course_list
        
        grouped_modules = df.groupby('course')['module'].apply(lambda x: ', '.join(x)).reset_index()
        for description in range(len(df['course_description'])):
            course_value = df.loc[description, 'course']
            module_list = grouped_modules[grouped_modules['course'] == course_value]['module'].values[0]
            df.loc[description, 'course_description'] += '. Modules available in this course are ' + module_list

        batch_size = 100
        ids = [f'course_id_{i}' for i in range(len(df))]

        for i in range(0, len(df), batch_size):
            i_end = min(len(df), i + batch_size)
            batch = df.iloc[i:i_end].copy()
            batch['text'] = batch.apply(
                lambda record: f"{record['campus']} {record['campus_description']} {record['course']} {record['course_description']} {record['module']} {record['module_description']}", 
                axis=1
            )
            metadatas = [
                {
                    'campus': record['campus'],
                    'campus_description': record['campus_description'],
                    'course': record['course'],
                    'course_description': record['course_description'],
                    'module': record['module'],
                    'module_description': record['module_description'],
                    'text': record['text']
                }
                for _, record in batch.iterrows()
            ]

            documents = batch['text'].tolist()
            embeds = embed.embed_documents(documents)
            
            try:
                index.upsert(vectors=zip(ids[i:i_end], embeds, metadatas))
            except:
                if index_name not in pc.list_indexes().names():
                    pc.create_index(
                        name=index_name,
                        dimension=1536,
                        metric='dotproduct',
                        spec=ServerlessSpec(cloud='aws', region='us-east-1')
                    )
                    index.upsert(vectors=zip(ids[i:i_end], embeds, metadatas))
        return {"status": "Data inserted successfully!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")

async def stream_agent_response(content: str):
    try:
        buffer = ""
        for chunk in agent.run(content):
            buffer += chunk 
            while " " in buffer: 
                word, buffer = buffer.split(" ", 1) 
                yield word+" "
                await asyncio.sleep(0.1)
        if buffer:
            yield buffer
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in streaming: {str(e)}")

@app.websocket("/user_query")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            async for response_chunk in stream_agent_response(data):
                await websocket.send_text(response_chunk)
    except WebSocketDisconnect as e:
        await websocket.close()
        raise HTTPException(status_code=500,detail=f"Web socket disconnected: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)