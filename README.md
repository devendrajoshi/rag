# RAG for LLM: A Dockerized Implementation

This repository contains a **learning-focused implementation** of **Retrieval-Augmented Generation (RAG)** for **Language Model (LLM)**. The primary goal of this project is to provide an educational resource for understanding and experimenting with RAG and LLM in question-answering tasks. While the implementation is dockerized for ease of use and deployment, it is intended for learning purposes only. **The author assumes no liability for any use of this code beyond educational purposes.**

## Components

The project consists of two main components:

1. **Ollama Container**: This container runs the Ollama service, which is responsible for interacting with local LLM. The Docker Compose configuration for this container is as follows:

    ```yaml
    ollama:
      build:
        context: .
        dockerfile: Dockerfile.ollama
      container_name: ollama-container
      ports:
        - "11434:11434"
      volumes:
        - ${HOST_OLLAMA_HOME}:/root/.ollama
      restart: always
    ```

    - This container builds from the `Dockerfile.ollama`, which extends the official `ollama/ollama` image to handle some certificate issues. In normal scenarios, you can use the official image directly.
    - It maps port 11434 on the host to port 11434 in the container.
    - It mounts a volume from the host to the container to persist data. `${HOST_OLLAMA_HOME}` is where the LLM files will be dowloaded.

2. **FastAPI Container**: This container runs the FastAPI service, which provides the API endpoints for interacting with the RAG system. It depends on the Ollama container to function correctly. The Docker Compose configuration for this container is as follows:

    ```yaml
    fastapi:
      build:
        context: .
        dockerfile: Dockerfile.fastapi
      container_name: fastapi-container
      restart: always
      depends_on:
        - ollama
      ports:
        - "9001:9001"
      volumes:
        - ${HOST_INDEX_PATH}:${INDEX_PATH}
        - ${HOST_DOCS_PATH}:${LOCAL_DOCS_PATH}
    ```

    - This container builds from the `Dockerfile.fastapi` and maps port 9001 on the host to port 9001 in the container.
    - It mounts two volumes from the host to the container:
        - `${HOST_INDEX_PATH}:${INDEX_PATH}`: This is the path where the index files (vector database) are stored. The default value is `./index/`.
        - `${HOST_DOCS_PATH}:${LOCAL_DOCS_PATH}`: This is the path where the user-provided PDFs are located. These PDFs are used for creating embeddings and stored in the vector database.
    - See the **Environment Variables** section for details on `${HOST_INDEX_PATH}`, `${INDEX_PATH}`, `${HOST_DOCS_PATH}`, and `${LOCAL_DOCS_PATH}`.

These configurations ensure that both services are properly set up and can communicate with each other, providing a robust environment for experimenting with Retrieval-Augmented Generation and Language Models.

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
docker-compose up --build
```

This will start the Ollama and FastAPI services, and the application will be accessible at `http://localhost:9001`.

## Note

This repository is intended for learning purposes. Please use it accordingly and responsibly. 

This document describes the API for a simple server using the RAG (Retriever-Augmented Generation) approach.

### Technologies Used

* FastAPI: Web framework used to build the API. ([https://github.com/fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template))
* OllamaLLM: Library for interacting with a Large Language Model (LLM). (Specific library documentation might be needed)
* (Optional) Retriever: Library for retrieving relevant documents from a database based on the prompt.

### API Endpoints

* **/debug/** (GET): This endpoint returns information about the environment variables used by the application.
* **/create_index/** (POST): This endpoint triggers the creation of a document index in the background. 
* **/query/** (POST): This endpoint takes a query in the request body and generates a response using the RAG approach.

### Data Models

* **RequestModel**: This model defines the data expected in the request body for the **/query/** endpoint.
    * **prompt (str):** This field is mandatory and specifies the user's query.
    * **prompt_template (Optional[str]):** This optional field allows the user to provide a custom prompt template for the RAG chain. 
    * **session_context (Optional[str]):** This optional field allows the user to provide context for the current conversation.

### API Details

* **/debug/**: This endpoint returns a dictionary containing information about the following environment variables:
    * INDEX_PATH: Path to the document index.
    * LLM_MODEL: Name of the LLM model used.
    * LLM_HOST: Hostname of the LLM server. 
    * LLM_PORT: Port of the LLM server.
    * RAG_PROMPT_TEMPLATE_TXT: Default prompt template used for the RAG chain.
    * SPLITTER_CHUNK_SIZE:  (Optional) Chunk size for splitting documents during retrieval (if a retriever is used).
    * SPLITTER_CHUNK_OVERLAP: (Optional) Overlap between chunks for splitting documents during retrieval (if a retriever is used).
    * LOCAL_DOCS_PATH: (Optional) Path to a local folder containing documents (if a retriever is used).
    This endpoint also attempts to check the status of the LLM server and retrieves a list of available models (if possible).

* **/create_index/**: This endpoint triggers the creation of a document index in the background. If the index creation process is already running, it will return a message indicating that. Otherwise, it will start the process in the background and return a message indicating that the creation has been initiated.

* **/query/**: This endpoint takes a query in the request body and generates a response using the RAG approach.
    * **Request Body**: The request body should contain data in the format specified by the `RequestModel` class.
    * **Process**:
        1. The endpoint checks if a session context is provided and builds the local prompt by combining the session context with the user's query.
        2. It attempts to retrieve relevant documents from the document index using the retriever (if available).
        3. If no documents are retrieved, the prompt is sent directly to the LLM for generation.
        4. If documents are retrieved:
            * A prompt template (either the default or the user-provided one) is used to format the retrieved documents and the user's query.
            * The formatted prompt is then sent through a chain of processing steps:
                * The retriever is used to retrieve relevant passages from the formatted documents.
                * The prompt template is used to format the retrieved passages and the user's query into a prompt suitable for the LLM.
                * The LLM generates a response based on the formatted prompt.
                * Finally, the response is parsed and returned.
    * **Response**: The endpoint returns a dictionary containing the following information:
        * **response (str)**: The generated response from the LLM.
        * **session_context (str)**: The provided session context (if any).
    * **Error Handling**: In case of any exceptions during processing, the endpoint logs the error and raises an HTTPException with a status code of 500 and the error message.


### Additional Notes

* This documentation assumes basic familiarity with FastAPI and the RAG approach.
* Refer to the specific library documentations (OllamaLLM, Retriever) for detailed information on their functionalities. 

## Additional Documentation for Document Indexing

### Environment Variable: SPLITTER_CHUNK_OVERLAP

* This section explains the environment variable `SPLITTER_CHUNK_OVERLAP` and its usage in document indexing.

**Variable Name:** SPLITTER_CHUNK_OVERLAP

**Default Value:** 200 (can be overridden by setting the environment variable)

**Data Type:** Integer

**Description:** This variable defines the overlap between chunks of text when splitting documents during indexing. 

**Explanation:**

The `create_index` function utilizes a `RecursiveCharacterTextSplitter` to split large documents into smaller chunks for processing. This variable controls the amount of overlap between these chunks. A positive overlap value ensures that the ending of one chunk overlaps with the beginning of the next chunk.

**Benefits of Overlap:**

* Overlap helps to avoid missing information at the boundaries between chunks.
* It can be particularly useful for tasks like sentence retrieval, where a complete sentence might span across multiple chunks.

**Impact on Performance:**

* Increasing the overlap value can improve retrieval accuracy but also increases processing time and memory usage during indexing.
* A smaller overlap value can be faster but might lead to missing information at chunk boundaries.

**Recommendation:**

The optimal overlap value depends on the specific use case and the size of your documents. A value between 100 and 200 characters is a common starting point. You can experiment with different values to find the best balance between accuracy and performance for your needs.


### Document Indexing Functions

This section describes the functions involved in creating the document index:

* **get_vector_db()**: This function retrieves a vector database instance for storing document embeddings. It uses the `EMBEDDING_MODEL_NAME` environment variable to specify the model for generating embeddings.

* **create_index()**: This function is responsible for the overall document indexing process. It performs the following steps:
    1. Retrieves a vector database instance using `get_vector_db()`.
    2. Clears any existing documents from the database.
    3. Checks the `LOCAL_DOCS_PATH` environment variable to determine the location of documents.
    4. Calls appropriate functions (`read_local_files` or `read_s3_files`) to process documents based on the path format.
    5. Logs the total number of indexed documents.

* **process_pdf(file, source, doc_cnt)**: This function processes a single PDF document. It uses the `PyPDF2` library to extract text and splits it into chunks using the `splitter` object (created with `SPLITTER_CHUNK_SIZE` and `SPLITTER_CHUNK_OVERLAP`). 

* **read_local_files(vector_db)**: This function handles reading and processing PDF documents from a local directory specified by `LOCAL_DOCS_PATH`. It iterates through all files with the `.pdf` extension and calls `process_pdf` for each file.

* **read_s3_files(vector_db)**: This function handles reading and processing PDF documents from an S3 bucket. It parses the `LOCAL_DOCS_PATH` to extract bucket and document path information. It then uses the `boto3` library to interact with S3, download documents, and process them using `process_pdf`.


By understanding these functions and the `SPLITTER_CHUNK_OVERLAP` variable, you can gain a deeper understanding of the document indexing process in this API.

