import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
import PyPDF2
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from datetime import datetime
import requests


load_dotenv()

# Load environment variables
INDEX_PATH = os.getenv('INDEX_PATH', './index/')
EMBEDDING_MODEL_NAME = os.getenv('EMBEDDING_MODEL_NAME', 'sentence-transformers/all-mpnet-base-v2')
LOCAL_DOCS_PATH = os.getenv('LOCAL_DOCS_PATH', './localdocs/')
#LOCAL_DOCS_PATH = os.getenv('LOCAL_DOCS_PATH', 's3://dataseek.dev.net/rag_docs/')
SPLITTER_CHUNK_SIZE = int(os.getenv('SPLITTER_CHUNK_SIZE', 1000))
SPLITTER_CHUNK_OVERLAP = int(os.getenv('SPLITTER_CHUNK_OVERLAP', 200))

splitter = RecursiveCharacterTextSplitter(chunk_size=SPLITTER_CHUNK_SIZE, chunk_overlap=SPLITTER_CHUNK_OVERLAP)


def get_vector_db():
    requests.packages.urllib3.disable_warnings()
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vector_db = Chroma(
        collection_name="local_collection",
        embedding_function=embeddings,
        persist_directory=INDEX_PATH+"embeddings_db",  # Where to save data locally, remove if not neccesary
    )
    return vector_db


def create_index():
    current_time = datetime.now()
    vector_db = get_vector_db()
    #empty the vector_db before adding new documents
    vector_db.reset_collection()
    doc_cnt = 0
    doc_cnt = read_local_files(vector_db)
    print(f"Indexed {doc_cnt} documents in {datetime.now() - current_time}")

def process_pdf(file, source, doc_cnt):
    global splitter
    documents = []
    id_cnt = doc_cnt
    reader = PyPDF2.PdfReader(file)
    text = ''
    page_cnt = 0
    for page in range(len(reader.pages)):
        text = reader.pages[page].extract_text()
        page_cnt += 1
        for chunk in splitter.split_text(text):
            id_cnt += 1
            doc = Document(
                page_content=chunk,
                metadata={"source": source, "page": page_cnt},
                id=id_cnt,
            )
            documents.append(doc)
    print(f"Read {page_cnt} pages")
    return documents

def read_local_files(vector_db):
    doc_cnt = 0
    for filename in os.listdir(LOCAL_DOCS_PATH):
        if filename.endswith('.pdf'):
            with open(os.path.join(LOCAL_DOCS_PATH, filename), 'rb') as file:
                print(f"Reading {filename}")
                docs = process_pdf(file, filename, doc_cnt)
                doc_cnt += len(docs)
                vector_db.add_documents(documents=docs)
    return doc_cnt