# CV Adapter 🚀

> **Experiment Alert**: This entire project was created using Cursor as an AI-powered coding experiment. Not a single line of code was written manually - everything was generated through AI assistance!

**🌐 Live Demo**: [cv2job.online](https://cv2job.online)

An intelligent CV adaptation tool that uses AI to tailor your resume for specific job descriptions. Built with FastAPI and React, this application helps job seekers optimize their CVs to better match job requirements.

## ✨ Features

- **AI-Powered CV Adaptation**: Uses OpenAI's GPT models to intelligently adapt your resume
- **PDF Upload Support**: Upload your CV as a PDF and get an adapted version back
- **Multiple Adaptation Strategies**: Choose from different approaches to tailor your CV
- **Real-time Processing**: Fast API responses for seamless user experience
- **Modern UI**: Clean, responsive React interface
- **Containerized Deployment**: Single Docker container for easy deployment
- **No Database Required**: Stateless design for simplicity

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **OpenAI API** - GPT models for CV adaptation
- **PyPDF** - PDF text extraction
- **ReportLab** - PDF generation
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Modern CSS** - Responsive design

### Infrastructure
- **Docker** - Containerization
- **Railway** - Cloud deployment platform

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/cv-adapter.git
   cd cv-adapter
   ```

2. **Set up environment variables**
   ```bash
   export OPENAI_API_KEY=sk-your-openai-api-key
   ```

3. **Backend setup**
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r backend/requirements.txt
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

4. **Frontend setup** (in a new terminal)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Docker Deployment

```bash
# Build the image
docker build -t cv-adapter .

# Run the container
docker run --rm -e OPENAI_API_KEY=$OPENAI_API_KEY -p 8000:8000 cv-adapter
```

Access at http://localhost:8000

## 📁 Project Structure

```
cv-adapter/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   │   └── routes.py   # Main endpoints (/healthz, /adapt, /adapt-upload)
│   │   ├── core/           # Core functionality
│   │   │   ├── config.py   # Configuration management
│   │   │   ├── llm.py      # OpenAI integration
│   │   │   └── pdf.py      # PDF processing utilities
│   │   ├── models/         # Data models
│   │   │   └── schemas.py  # Pydantic schemas
│   │   └── main.py         # FastAPI app entry point
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.tsx         # Main React component
│   │   ├── api.ts          # API client
│   │   ├── main.tsx        # React entry point
│   │   └── styles.css      # Styling
│   ├── package.json        # Node.js dependencies
│   └── vite.config.ts      # Vite configuration
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Docker Compose configuration
└── railway.toml           # Railway deployment config
```

## ⚙️ Configuration

Configure the application using environment variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | - | ✅ |
| `CV_ADAPTER_OPENAI_MODEL` | OpenAI model to use | `gpt-4o-mini` | ❌ |
| `CV_ADAPTER_OPENAI_TEMPERATURE` | Model temperature | `0.2` | ❌ |
| `CV_ADAPTER_OPENAI_MAX_OUTPUT_TOKENS` | Max output tokens | `800` | ❌ |

## 🌐 API Endpoints

### Health Check
```
GET /api/healthz
```
Returns application health status.

### Adapt Resume (Text)
```
POST /api/adapt
Content-Type: application/json

{
  "resume_text": "Your resume content...",
  "job_description": "Job requirements...",
  "strategy": "professional"
}
```

### Adapt Resume (PDF Upload)
```
POST /api/adapt-upload
Content-Type: multipart/form-data

file: [PDF file]
job_description: "Job requirements..."
strategy: "professional"
```

Returns an adapted PDF file.

## 🚀 Deployment

### Railway (Recommended)

This project is optimized for Railway deployment:

1. **Connect Repository**: Link your GitHub repository to Railway
2. **Set Environment Variables**:
   - `OPENAI_API_KEY` (required)
   - Optional: model configuration variables
3. **Deploy**: Railway automatically uses the `Dockerfile` and `railway.toml`

The app will be available at your Railway-provided URL with automatic:
- SSL certificates
- Health checks via `/api/healthz`
- Container restarts
- Port configuration

### Manual Railway CLI

```bash
npm install -g @railway/cli
railway login
railway link  # or railway init for new project
railway up
```

### Other Platforms

The Docker container can be deployed on any platform supporting containers:
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- DigitalOcean App Platform
- Heroku

## 🤝 Contributing

Since this is an AI-generated experiment, contributions are welcome to:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines

- Follow existing code patterns (even if AI-generated!)
- Add tests for new features
- Update documentation as needed
- Ensure Docker builds successfully

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Cursor](https://cursor.sh/)** - The AI-powered editor that made this project possible
- **OpenAI** - For providing the GPT models that power the CV adaptation
- **FastAPI** - For the excellent Python web framework
- **React** - For the robust frontend library
- **Railway** - For seamless deployment infrastructure

## 🔮 Future Enhancements

- [ ] Support for multiple file formats (DOCX, TXT)
- [ ] Advanced prompt templates and evaluation metrics
- [ ] User authentication and session management
- [ ] CV template library
- [ ] Batch processing capabilities
- [ ] Analytics and adaptation insights
- [ ] Multi-language support

## 📞 Support

- **Live Demo**: [cv2job.online](https://cv2job.online)
- **Issues**: [GitHub Issues](https://github.com/yourusername/cv-adapter/issues)
- **Documentation**: [API Docs](https://cv2job.online/docs)

---

**⚡ Powered by AI** | **🚀 Built with Cursor** | **🌐 Deployed on Railway** 