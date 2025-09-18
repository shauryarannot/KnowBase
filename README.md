# 📘 KnowBase
> AI-Powered Knowledge Base for Courses, Campuses, Faculty & Modules

KnowBase is an AI-driven academic search engine that makes it effortless to explore and connect knowledge across **campuses, courses, faculty, and modules**. It transforms structured data into semantic embeddings, enabling natural language search and intelligent retrieval of information.  

---

## ✨ Features
- 🔍 **Semantic Search** – Ask natural questions, get meaningful results  
- 🏫 **Campus-wide Indexing** – Organizes content by campus, courses, faculty, and modules  
- 🤖 **AI Embeddings** – Powered by vector search for context-aware retrieval  
- 📚 **Scalable Knowledge Base** – Handles growing datasets seamlessly  
- ⚡ **Fast Retrieval** – Optimized batching and vector indexing  

---

## 🏗️ Tech Stack
- **Python** – Core data processing  
- **Pandas** – Data handling & transformation  
- **LangChain** – AI pipelines (embeddings, query processing)  
- **Chroma / Pinecone** – Vector database for indexing and search  
- **OpenAI Embeddings** – Semantic representation of course data  

---

## 📂 Dataset Structure
KnowBase expects a JSON dataset in the following format:

```json
{
  "content": [
    {
      "campus": "Campus Name",
      "campus_description": "Description of the campus",
      "courses": [
        {
          "course": "Course Name",
          "course_description": "Description of the course",
          "faculty": [
            {
              "faculty_name": "Faculty Name",
              "faculty_bio": "Short bio"
            }
          ],
          "modules": [
            {
              "module": "Module Name",
              "module_description": "Description of the module"
            }
          ]
        }
      ]
    }
  ]
}
````

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/your-username/KnowBase.git
cd KnowBase
```

Create a virtual environment & install dependencies:

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

Set up environment variables in `.env`:

```env
OPENAI_API_KEY=your_openai_api_key
```

---

## 🚀 Usage

1. **Prepare the dataset** (`course.json`).
2. **Run the embedding pipeline**:

   ```bash
   python index_data.py
   ```
3. **Start search queries**:

   ```bash
   python query.py "Find all AI-related modules in Delhi campus"
   ```

---

## 📊 Example Query

**Input:**

```bash
python query.py "Who teaches Data Structures in Bangalore campus?"
```

**Output:**

```
Campus: Bangalore
Course: Computer Science
Faculty: Dr. Meera Sharma
Module: Data Structures
```

---

## 🛠️ Roadmap

* [ ] Add **UI for search** (React/Streamlit)
* [ ] Support for **PDF/Doc ingestion**
* [ ] Multi-language search support
* [ ] Deploy with **Docker + Cloud DB**

---

## 🤝 Contributing

Contributions are welcome! Fork the repo, make changes, and submit a PR.

---

## 📜 License

MIT License – feel free to use and adapt.

```
