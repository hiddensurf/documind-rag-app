# DocuMind Backend API

FastAPI backend for DocuMind RAG Document Assistant.

## Setup

1. **Create virtual environment:**
```bash
   python3 -m venv venv
   source venv/bin/activate
```

2. **Install dependencies:**
```bash
   pip install -r requirements.txt
```

3. **Configure environment:**
```bash
   cp .env.example .env
   # Edit .env with your API keys
```

4. **Run development server:**
```bash
   uvicorn app.main:app --reload
```

5. **Access API docs:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

- `POST /api/documents/upload` - Upload document
- `GET /api/documents` - List documents
- `DELETE /api/documents/{id}` - Delete document
- `POST /api/chat` - Chat with documents
- `POST /api/mindmap` - Generate mind map
- `GET /api/health` - Health check

## Project Structure
```
backend/
├── app/
│   ├── api/          # API routes
│   ├── core/         # Configuration
│   ├── models/       # Pydantic models
│   ├── services/     # Business logic
│   └── utils/        # Utilities
├── uploads/          # Uploaded files
├── .env             # Environment variables
└── requirements.txt  # Dependencies
```
