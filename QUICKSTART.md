# Quick Start Guide

Get iOps running locally in 5 minutes.

## Prerequisites

- Python 3.11+
- Node.js 18+
- Git

## Installation

### 1. Clone & Navigate
```bash
git clone https://github.com/yourusername/iOps.git
cd iOps
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
```

### 4. Environment Setup

**Backend** - Create `backend/.env`:
```env
DATABASE_URL=sqlite:///./iops.db
SECRET_KEY=your-secret-key-here
GROQ_API_KEY=your-groq-api-key
RESEND_API_KEY=your-resend-api-key
ENVIRONMENT=development
DEBUG=true
```

**Frontend** - Create `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
```

## Running

### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate  # or .\venv\Scripts\activate
uvicorn main:app --reload
```

Backend runs at: `http://localhost:8000`

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

Frontend runs at: `http://localhost:5173`

## Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm run test
```

## Common Commands

### Backend
```bash
# Run migrations
python migrate.py

# Reset database
rm iops.db

# Run specific test
pytest tests/test_short_code_generation.py -v

# Check code style
flake8 .
```

### Frontend
```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Format code
npm run format
```

## Troubleshooting

### Port Already in Use
```bash
# Backend (change port)
uvicorn main:app --reload --port 8001

# Frontend (Vite auto-selects if 5173 is taken)
npm run dev
```

### Database Issues
```bash
# Reset database
rm backend/iops.db
python backend/migrate.py
```

### Module Not Found
```bash
# Reinstall dependencies
cd backend
pip install -r requirements.txt --force-reinstall

cd ../frontend
npm install --force
```

### CORS Errors
Ensure `VITE_API_URL` in `frontend/.env` matches your backend URL.

## Project Structure

```
iOps/
├── backend/          # FastAPI backend
│   ├── routers/     # API endpoints
│   ├── utils/       # Utilities
│   ├── tests/       # Tests
│   └── main.py      # Entry point
├── frontend/        # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
└── README.md
```

## Next Steps

1. Read [README.md](README.md) for full documentation
2. Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
3. Review [.kiro/specs/](./kiro/specs/) for feature details
4. Explore API at `http://localhost:8000/docs`

## Need Help?

- 📖 [Full Documentation](README.md)
- 🤝 [Contributing Guide](CONTRIBUTING.md)
- 🐛 [Report Issues](https://github.com/yourusername/iOps/issues)
- 💬 [Discussions](https://github.com/yourusername/iOps/discussions)

---

Happy coding! 🚀
