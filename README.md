# RAG for LLM: A Dockerized Implementation

This repository contains the implementation of **Retrieval-Augmented Generation (RAG)** for **Language Model (LLM)**. The goal of this project is to provide a robust and efficient solution for question-answering tasks using RAG and LLM. The implementation is dockerized for ease of use and deployment.

## Components

The project consists of two main components:

1. **Ollama Container**: This container runs the Ollama service. The Docker Compose configuration for this container is as follows:

```yaml
ollama:
    image: ollama:latest
    container_name: ollama-container
    restart: always
```

2. **FastAPI Container**: This container runs the FastAPI service and depends on the Ollama container. The Docker Compose configuration for this container is as follows:

```yaml
fastapi:
    build: .
    container_name: fastapi-container
    restart: always
    depends_on:
      - ollama
    ports:
      - "8000:8000"
```

## Environment Variables

The application uses the following environment variables, which can be overridden by the user when starting the Docker containers:

- `INDEX_PATH`: This is the path where the index files are stored. The default value is `./index/`.
- `EMBEDDING_MODEL_NAME`: This is the name of the model used for generating embeddings. The default model is `sentence-transformers/all-mpnet-base-v2`.
- `LOCAL_DOCS_PATH`: This is the directory where the application looks for PDF files to create embeddings and store them in a vector database. The default path is `./localdocs/`. Users should mount their folder containing their PDF files to the FastAPI container.
- `SPLITTER_CHUNK_SIZE`: This is the size of the chunks that the document splitter will create. The default chunk size is `1000`.
- `SPLITTER_CHUNK_OVERLAP`: This is the overlap between chunks that the document splitter will create. The default overlap is `200`.
- `LLM_MODEL`: This is the name of the LLM model used. The default model is `llama3.1`.
- `LLM_HOST`: This is the host address for the LLM service. The default host is `127.0.0.1`.
- `LLM_PORT`: This is the port number for the LLM service. The default port is `11434`.
- `RAG_PROMPT_TEMPLATE_TXT`: This is the prompt template text for the RAG model. The default text is "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use five sentences maximum and keep the answer concise."

## Usage

To run the application, use Docker Compose:

```bash
docker-compose up
```

This will start the Ollama and FastAPI services, and the application will be accessible at `http://localhost:8000`.

## Note

This repository is intended for learning purposes. Please use it accordingly and responsibly. 

Happy coding! 🚀
