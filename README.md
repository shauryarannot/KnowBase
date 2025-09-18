# Chatbot API Documentation

Chatbot API, which is designed to manage and retrieve knowledge about campuses, courses, and modules using OpenAI’s language model and Pinecone’s vector storage.

# Requirements :

This API uses the following key libraries:

- FastAPI: Web framework to handle HTTP requests and WebSocket connections.
- Pinecone: Vector database for efficient knowledge retrieval.
- LangChain: Framework to build language model-powered applications.
- dotenv: Loads environment variables from a .env file.
- pandas: Data manipulation and analysis tool.

# Environment Variables

Before running the API, set up the following environment variables in a .env file:

- OPENAI_API_KEY: API key for OpenAI.
- PINECONE_API_KEY: API key for Pinecone.

# Endpoints

1. Root Endpoint

- Path: /
- Method: GET
- Description: Provides information about available endpoints and usage examples.
- Response:
  json
  {
  "message": "Chatbot API",
  "usage": "Send a POST request to the /insert_data/ endpoint with a json file to insert data into
  vector database and /user_query/ for query.",
  "example1": {
  "endpoint": "/insert_data/",
  "method": "POST",
  "file_type": "json"
  },
  "example2": {
  "endpoint": "/user_query/"
  }
  }

2. Insert Data Endpoint

- Path: /insert_data/
- Method: POST
- Parameters:
  - file: An uploaded JSON file containing campus, course, and module details.
- Description:
  - Reads and structures data from the uploaded JSON file.
  - Structures data into rows and then organizes it by campus and course.
  - Creates a combined description for each campus and course, specifying the available courses and modules.
  - Embeds each text document and stores it in the Pinecone vector database.
- Response:
  - Returns a success message on successful data insertion.
- Example:
  json
  {
  "status": "Data inserted successfully!"
  }

3. WebSocket User Query Endpoint

- Path: /user_query
- Method: WebSocket
- Description:
  - Receives queries from a WebSocket connection.
  - Uses a language model agent to process queries and return streaming responses.
  - Sends chunks of responses back to the WebSocket client in real time.
- Example Usage:
  - Connect to the WebSocket endpoint at /user_query.
  - Send a query as a text message, and receive a streamed response.

# Key Components

1. Pinecone Setup

- Pinecone Client: The Pinecone client (pc) is initialized with the PINECONE_API_KEY.
- Index Creation: Checks if the index chatbot-knowledge-base exists. If not, it creates it with 1536
  dimensions, using the dotproduct metric.

2. LangChain Components

- Embeddings: Uses OpenAIEmbeddings to embed text data for vector storage in Pinecone.
- VectorStore: Stores embedded text data in Pinecone for efficient retrieval.
- Language Model: Uses OpenAI’s GPT-3.5 Turbo model via ChatOpenAI to process queries and retrieve information from vector storage.
- Memory: Stores conversation history with ConversationBufferWindowMemory, retaining the last 7 messages.
- RetrievalQA: A question-answering chain that retrieves information from the vector store and summarizes responses.

3. Agent

- Tools: Defines a tool named "Knowledge Base" that interacts with the vector store for retrieving and answering general knowledge queries.
- Agent Initialization: Initializes an agent with the tool, language model, and conversation memory. The agent provides conversational responses based on the user query and retrieved knowledge.

# Endpoint Logic

Insert Data Logic (/insert_data/):

1. Reads JSON Data: Extracts campus, course, and module information from the uploaded file.
2. Structures Data:
   - Organizes data by campus and course for easy retrieval.
   - Appends a list of available courses to each campus_description and modules to each
     course_description.
3. Embeds Data: Creates embeddings for the combined descriptions and stores them in Pinecone as vectors, with batch insertion for efficiency.

User Query Logic (/user_query WebSocket):

1. WebSocket Connection: Accepts a WebSocket connection.
2. Streamed Response:
   - Processes the query with the agent, returning a streamed response.
   - Chunks the agent’s response word by word, sending it back in real time.
3. Error Handling: Handles errors gracefully and closes the WebSocket connection in case of a disconnection or error.

Helper Functions:
stream_agent_response(content: str) -> AsyncIterable[str]

- Description: Sends chunks of agent responses by streaming each word.
- Parameters:
  - content: Query content sent to the agent.
- Yields: Response in word chunks.
  Example JSON File Format for /insert_data/
  To insert data, provide a JSON file structured as follows:
  json
  {
  "content": [
  {
  "title": "Main Campus",
  "description": "The main campus of the university.",
  "courses": [
  {
  "title": "Computer Science",
  "description": "CS course description",
  "modules": [
  {
  "title": "Intro to Programming",
  "description": "Introduction to programming concepts"
  },
  .
  .
  ]
  }
  ]
  }
  ]
  }

## Running the API

1. Install Dependencies: Ensure you install FastAPI, Pinecone, LangChain, and other required libraries.

- pip install -r requirements.txt

2. Run the Application: Use Uvicorn to start the FastAPI server.
   bash
   uvicorn your_file_name:app --host 0.0.0.0 --port 8000
3. Testing the API: Visit http://localhost:8000 to check the root endpoint and review instructions for
   using /insert_data/ and /user_query endpoints.
   This documentation provides an overview of each component and endpoint to help you understand, set
   up, and use the Chatbot API effectively.
