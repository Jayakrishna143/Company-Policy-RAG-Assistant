#  Company Policy RAG Assistant

A RAG (Retrieval-Augmented Generation) based chatbot that lets you upload company policy PDFs and ask questions about them. Built with FastAPI as the backend and Streamlit as the frontend, powered by local LLMs via Ollama.

---

## How It Works

```
User → Streamlit → FastAPI → FAISS Vector DB → Ollama LLM → Answer
```

1. You upload PDF files through the Streamlit interface
2. FastAPI processes and chunks the PDFs, then stores them as vectors in a FAISS database
3. When you ask a question, the most relevant chunks are retrieved
4. Ollama's LLM reads those chunks and gives you an answer based only on what's in the documents

---

## Prerequisites

Before running this project, make sure you have:

- Python 3.9 or higher
- [Ollama](https://ollama.com) installed and running on your machine

Pull the required models:

```bash
ollama pull nomic-embed-text
ollama pull gemma3:1b
```

---

## Installation

```bash
git clone https://github.com/Jayakrishna143/Company-Policy-RAG-Assistant.git
cd your-repo-name
pip install -r requirements.txt
```

---

## Project Structure

```
Rag_model/
├── server.py           # FastAPI backend (all the logic lives here)
├── streamlit.py        # Streamlit frontend (UI)
├── requirements.txt    # Python dependencies
├── .gitignore
├── vectordb/           # Created automatically after first PDF upload
└── temp_uploads/       # Created automatically, deleted after processing
```

---

## How to Run

**Step 1: Start Ollama**
```bash
ollama serve
```

**Step 2: Start the FastAPI server (in a new terminal)**
```bash
python server.py
```

Server runs at: `http://localhost:8000`

You can test all endpoints at: `http://localhost:8000/docs`

**Step 3: Start the Streamlit app (in another terminal)**
```bash
streamlit run streamlit.py
```

---

## How to Use

**First time (no database):**
1. Open the Streamlit app in your browser
2. You will see a file uploader since no database exists yet
3. Upload one or more PDF files
4. Click "Process PDFs"
5. Wait for the database to be created

**After database is created:**
1. Type your question in the text box
2. Hit Enter
3. You get an answer based only on the uploaded documents
4. Expand "View Sources" to see which parts of the documents were used

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/check-database` | Checks if a vector database exists |
| POST | `/ingest` | Upload PDFs and create the database |
| POST | `/ask` | Send a question and get an answer |

You can test all of these manually at `http://localhost:8000/docs`

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| FastAPI | Backend server and API |
| Streamlit | Frontend UI |
| LangChain | Document loading, chunking, and chaining |
| FAISS | Vector database for storing embeddings |
| Ollama | Running LLMs locally |
| nomic-embed-text | Embedding model |
| gemma3:1b | LLM for generating answers |

---

## Security Note

Sources are only shown when the LLM actually finds a relevant answer. If someone asks a question that has no answer in the documents, no document content is returned preventing accidental data exposure.

---

## .gitignore

Make sure your `.gitignore` includes the following so you don't accidentally push sensitive files:

```
vectordb/
temp_uploads/
*.pdf
__pycache__/
*.pyc
.env
```
