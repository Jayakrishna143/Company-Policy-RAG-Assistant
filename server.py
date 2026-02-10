import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

app = FastAPI()
DB_PATH = r"C:\Users\jayak\OneDrive\Desktop\fastapi\Rag_model\vectordb"
TEMP_UPLOAD_PATH = r"C:\Users\jayak\OneDrive\Desktop\fastapi\Rag_model\temp_uploads"
# Make sure temp folder exists
os.makedirs(TEMP_UPLOAD_PATH, exist_ok=True)


# Question model
class Question(BaseModel):
    question: str


# 1. Check if database exists
@app.get("/check-database")
def check_database():
    exists = os.path.exists(DB_PATH) and len(os.listdir(DB_PATH)) > 0
    return {"exists": exists}


# 2. Ingest PDFs and create database
@app.post("/ingest")
async def ingest_pdfs(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    try:
        documents = []

        for file in files:
            file_path = os.path.join(TEMP_UPLOAD_PATH, file.filename)

            # Save uploaded file
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            # Load PDF
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            documents.extend(pages)

        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(documents)

        # Create embeddings and save
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        db = FAISS.from_documents(chunks, embeddings)

        # Make sure directory exists
        os.makedirs(DB_PATH, exist_ok=True)
        db.save_local(DB_PATH)

        # Clean up temp files
        shutil.rmtree(TEMP_UPLOAD_PATH)
        os.makedirs(TEMP_UPLOAD_PATH, exist_ok=True)

        return {"message": "Database created successfully", "chunks": len(chunks)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 3. Answer questions
@app.post("/ask")
def ask_question(q: Question):
    # Check if DB exists
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=404, detail="Database not found")

    try:
        # Load database
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        db = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)

        # Setup retriever
        retriever = db.as_retriever(search_kwargs={"k": 3})
        llm = Ollama(model="gemma3:1b", temperature=0)

        # Get relevant documents
        docs = retriever.invoke(q.question)

        # Format context from retrieved documents
        context = "\n\n".join([doc.page_content for doc in docs])

        # Custom prompt
        template = """
Answer based ONLY on the context below.
If you don't know, say "I don't know based on the documents."

Context:
{context}

Question:
{question}

Answer:
"""
        prompt = PromptTemplate(template=template, input_variables=["context", "question"])

        # Create the chain manually
        chain = prompt | llm | StrOutputParser()

        # Get answer
        answer = chain.invoke({"context": context, "question": q.question})

        # Return answer and sources
        sources = [doc.page_content for doc in docs]

        return {
            "answer": answer,
            "sources": sources
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)