# Enterprise Knowledge Hub

A powerful Retrieval-Augmented Generation (RAG) system for enterprise knowledge management, built with LangChain, FastAPI, and FAISS vector store.

## Features

- 📄 Multi-format document ingestion (PDF, DOCX, TXT, CSV, XLSX)
- 🔍 Efficient vector similarity search using FAISS
- 🤖 Integration with Ollama for LLM capabilities
- 🚀 FastAPI-powered REST API
- 📦 Modular and extensible architecture

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai/) installed and running locally
- Virtual environment management tool (pipenv or venv)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Rishabh250/enterprise-knowledge-hub.git
cd enterprise-knowledge-hub
```

2. Create and activate a virtual environment:
```bash
# Using pipenv
pipenv install

# Or using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```env
VECTORSTORE_PATH=data/vectorstore
MODEL=llama2  # or your preferred Ollama model
```

## Project Structure

```
├── src/
│   ├── ingestion/          # Document loading and processing
│   ├── vectorstore/        # Vector store management
│   ├── rag/               # RAG pipeline implementation
│   └── scripts/           # Utility scripts
├── data/
│   ├── documents/         # Input documents
│   └── vectorstore/       # FAISS index storage
├── logs/                  # Application logs
└── app.py                # FastAPI application
```

## Usage

### 1. Set Up Project Directories

```bash
python src/scripts/setup.py
```

### 2. Ingest Documents

Place your documents in the `data/documents` directory, then run:

```bash
python src/scripts/ingest_documents.py --docs-dir data/documents
```

### 3. Test Query

To test the RAG pipeline directly:

```bash
python src/scripts/test_query.py
```

### 4. Run the API Server

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Query Endpoint

```bash
POST /query
Content-Type: application/json

{
    "query": "Your question here"
}
```

Response format:
```json
{
    "response": "Answer from the system",
    "sources": [
        {
            "source": "document_name.pdf"
        }
    ]
}
```

### Google Drive Integration

#### Ingest Files from Drive

```bash
POST /api/v1/ingest/drive/files
Content-Type: application/json

{
    "folder_id": "folder_id"
}
```

Response:
```json
{
    "status": "success",
    "message": "Successfully processed 2 files",
    "files_processed": [
        "data/documents/drive/document1.pdf",
        "data/documents/drive/document2.docx"
    ]
}
```

#### Ingest Folder from Drive

```bash
POST /api/v1/ingest/drive/folder/{folder_id}?recursive=true
```

Query Parameters:
- `recursive`: Whether to process subfolders (default: true)

Response:
```json
{
    "status": "success",
    "message": "Successfully processed 5 files",
    "files_processed": [
        "data/documents/drive/doc1.pdf",
        "data/documents/drive/subfolder/doc2.docx",
        "data/documents/drive/subfolder/doc3.txt"
    ]
}
```

## Supported Document Types

- PDF (`.pdf`)
- Word Documents (`.docx`)
- Text Files (`.txt`)
- Excel Spreadsheets (`.xlsx`, `.xls`)
- CSV Files (`.csv`)

## Development

### Adding New Document Types

Extend the `DocumentLoader` class in `src/ingestion/document_loader.py` to support additional document formats.

### Customizing the RAG Pipeline

Modify the prompt template and retrieval parameters in `src/rag/rag_pipeline.py` to adjust the system's behavior.

## Security Notes

- The vector store loading includes safety checks to prevent unauthorized deserialization
- Set `trust_source=True` only when loading vector stores from trusted sources
- Keep your `.env` file secure and never commit it to version control

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is open-sourced under the MIT License - see the LICENSE file for details.

---

This README provides a comprehensive overview of the project. Feel free to customize and extend it as needed for your specific use case.

### Google Drive Integration

To use Google Drive integration:

1. Create a Google Cloud Project:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Drive API

2. Create a Service Account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Fill in the details and create the account
   - Create a new key (JSON type) and download it
   - Save the JSON file as `keys/service-account.json` in your project

3. Share your Google Drive folders/files:
   - Share the folders or files you want to access with the service account email
   - The email will look like: `service-account-name@project-id.iam.gserviceaccount.com`

The Google Drive integration supports the same file types as local ingestion.
