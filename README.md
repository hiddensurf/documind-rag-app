# DocuMind - AI-Powered RAG Document Assistant

Advanced document analysis system with CAD support, multi-model AI analysis, and hybrid CV+LLM integration.

## 🎯 Features

### Core Features
- 📄 **Document Upload**: PDF, DOCX, TXT, CAD (DXF/DWG)
- 💬 **RAG Chat**: Query documents with AI-powered responses
- 🗺️ **Mind Maps**: Auto-generate Mermaid diagrams
- 🎨 **Dark Mode**: Beautiful dark/light theme switching

### CAD Analysis (Advanced)
- 🔍 **CAD Processing**: DXF/DWG parsing, SVG rendering
- 🤖 **Multi-Model AI**: 10+ AI models (Gemini, OpenRouter)
- 🔬 **Hybrid Analysis**: CV feature extraction + LLM reasoning
- ✨ **Vision Analysis**: 5-stage comprehensive CAD analysis

## 🏗️ Architecture
```
Frontend (React + Vite)
├── Mode Selector: Normal / Vision / Hybrid
├── Model Picker: Auto-select or choose specific model
└── Real-time Analysis UI

Backend (FastAPI + Python)
├── RAG Service: LlamaIndex + Pinecone
├── CAD Processing: ezdxf + matplotlib + cairosvg
├── CV Extractor: OpenCV + Tesseract OCR
├── Multi-Model Analyzer: Gemini + OpenRouter models
└── Hybrid Analyzer: CV + LLM integration
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Tesseract OCR
- API Keys: Google AI Studio, Pinecone, OpenRouter (optional)

### Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install system dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-eng

# Create .env file
cat > .env << 'ENVEOF'
GOOGLE_API_KEY=your_google_api_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=documind-index
OPENROUTER_API_KEY=your_openrouter_key  # Optional
LLM_MODEL=models/gemini-flash-latest
EMBEDDING_MODEL=models/text-embedding-004
CHUNK_SIZE=1024
CHUNK_OVERLAP=200
TOP_K=8
UPLOAD_DIR=uploads
ENVEOF

# Create required directories
mkdir -p uploads cad_uploads cad_renders cad_manifests conversations

# Start backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd .. # Back to root
npm install
npm run dev
```

Access: http://localhost:5173

## 🤖 AI Models Supported

### Vision Models (Image + Text)
- **Google Gemini 2.0 Flash** (Free, via AI Studio)
- **NVIDIA Nemotron Nano VL** (Free, via OpenRouter)
- **Qwen 2.5 VL 7B** (Free, via OpenRouter)

### Text-Only Models (CV-Assisted)
- **Llama 3.3 70B** (Free, 128K context)
- **Gemma 3 27B** (Free, fast)
- **GPT OSS 20B** (Free)
- **DeepSeek R1** (Paid, best reasoning)
- **Qwen 3 235B** (Paid, large model)

## 📊 Analysis Modes

### 1. Normal Chat (Default)
- Regular RAG query
- Searches all uploaded documents
- Fast responses

### 2. Vision Analysis (Advanced)
- 5-stage comprehensive analysis
- Uses vision AI models
- Detailed technical breakdown

### 3. Hybrid AI (CV + LLM)
- Computer vision feature extraction
- Works with text-only models
- Best for complex CAD analysis

## 🛠️ Project Structure
```
documind-rag-app/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI routes
│   │   ├── cad/           # CAD processing modules
│   │   │   ├── converter.py
│   │   │   ├── parser.py
│   │   │   ├── renderer.py
│   │   │   ├── cv_extractor.py
│   │   │   ├── multi_model_analyzer.py
│   │   │   └── hybrid_analyzer.py
│   │   ├── core/          # Configuration
│   │   ├── models/        # Data models
│   │   ├── services/      # Business logic
│   │   └── utils/         # Document loaders
│   ├── requirements.txt
│   └── .env
├── src/
│   ├── components/        # React components
│   ├── hooks/            # Custom hooks
│   ├── services/         # API client
│   └── context/          # React context
├── package.json
└── README.md
```

## 🔧 API Endpoints

### Documents
- `POST /api/documents/upload` - Upload document
- `GET /api/documents` - List documents
- `DELETE /api/documents/{id}` - Delete document

### Conversations
- `POST /api/conversations` - Create conversation
- `GET /api/conversations` - List conversations
- `POST /api/conversations/{id}/messages` - Send message

### AI Analysis
- `POST /api/conversations/{id}/advanced-analysis` - Vision analysis
- `POST /api/conversations/{id}/hybrid-analysis` - Hybrid CV+AI
- `GET /api/models` - List available AI models

## 📝 Development

### Running Tests
```bash
cd backend

# Test CV extraction
python test_cv_extractor.py

# Test multi-model analysis
python test_all_models.py

# Test hybrid analysis
python test_hybrid_analysis.py
```

### Adding New Models

Edit `backend/app/cad/multi_model_analyzer.py`:
```python
MODELS = {
    "your-model-id": {
        "name": "Your Model Name",
        "provider": "OPENROUTER",  # or "GEMINI"
        "capabilities": ["vision", "fast"],  # or ["reasoning"]
        "context_window": "128K tokens",
        "free": True,  # or False
        "notes": "Model description"
    }
}
```

## 🐛 Troubleshooting

### OpenRouter 401 Error
- Verify API key in `.env`
- Check key format: `sk-or-v1-...` (73 chars)
- Get new key: https://openrouter.ai/settings/keys

### Gemini Quota Exceeded
- Use OpenRouter Gemini as fallback
- Or use Hybrid mode with text-only models

### CAD Files Not Processing
- Ensure Tesseract is installed
- Check file permissions in `cad_renders/`
- Verify DXF file is valid

### Frontend Not Connecting
- Check backend is running on port 8000
- Verify CORS settings in `backend/app/core/config.py`
- Clear browser cache

## 📚 Technologies Used

### Backend
- **FastAPI** - Web framework
- **LlamaIndex** - RAG framework
- **Pinecone** - Vector database
- **ezdxf** - CAD file parsing
- **OpenCV** - Computer vision
- **Tesseract** - OCR
- **matplotlib/cairosvg** - Rendering

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Lucide React** - Icons
- **Mermaid** - Diagrams

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Google Gemini for AI capabilities
- OpenRouter for model access
- Pinecone for vector search
- Anthropic Claude for development assistance

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for better document analysis**
