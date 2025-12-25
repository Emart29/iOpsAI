# iOps - AI-Powered Data Science Copilot

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://react.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-MVP-orange.svg)]()

**Transform raw data into actionable insights with AI-powered analysis**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 🚀 Overview

**iOps** is a production-ready SaaS platform that democratizes data analysis through AI. Upload your data, ask questions in plain English, and get instant insights with beautiful visualizations—no coding required.

Built with a modern tech stack and designed for scalability, iOps combines the power of Large Language Models with robust data processing to deliver an intuitive analytics experience.

### Why iOps?

- **No Code Required**: Analyze data without writing SQL or Python
- **AI-Powered Insights**: Get intelligent recommendations and pattern discovery
- **Real-Time Collaboration**: Work with teammates on analyses simultaneously
- **Shareable Reports**: Generate public reports with custom URLs
- **Embeddable Charts**: Share visualizations anywhere on the web
- **Template Marketplace**: Reuse and monetize analysis workflows

---

## ✨ Key Features

### Core Analytics
- 📂 **Multi-Format Support**: CSV, Excel, JSON, and live data connectors
- 🤖 **AI Chat Assistant**: Ask questions about your data in natural language
- 📊 **AutoML Engine**: Automated machine learning for classification and regression
- 📈 **Interactive Visualizations**: Plotly charts with drill-down capabilities
- 🔍 **Exploratory Data Analysis**: Automatic pattern and anomaly detection

### Collaboration & Sharing
- 👥 **Real-Time Collaboration**: WebSocket-powered live editing with presence indicators
- 🔗 **Public Reports**: Generate shareable reports with unique short codes
- 🔐 **Password Protection**: Optional password-protected reports
- 📅 **Report Expiration**: Set expiration dates on public reports
- 🌐 **Embeddable Charts**: Embed visualizations on external websites

### Data Connectors
- 🔌 **Google Sheets**: Live sync with automatic refresh scheduling
- 🗄️ **Databases**: PostgreSQL and MySQL support with SQL query builder
- 📋 **Airtable**: Connect to Airtable bases
- 📥 **CSV URLs**: Fetch CSV files from URLs with scheduled updates

### Monetization
- 💳 **Stripe Integration**: Subscription billing with multiple tiers
- 🛍️ **Template Marketplace**: Buy and sell analysis templates
- 📊 **Revenue Tracking**: Monitor earnings and template performance
- 💰 **Payout Management**: Stripe Connect for creator payouts

### Enterprise Features
- 📈 **Admin Analytics Dashboard**: Comprehensive metrics and KPIs
- 🔒 **Security Hardening**: Input validation, rate limiting, encryption
- 📧 **Email Notifications**: Automated alerts for important events
- 🎯 **Usage Tracking**: Tier-based limits and quota management
- 🚀 **Production Deployment**: Ready for Vercel, Render, and Railway

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Real-Time**: Socket.io for WebSocket communication
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **Payments**: Stripe SDK
- **Email**: Resend or SendGrid
- **Monitoring**: Sentry for error tracking

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Charts**: Recharts and Plotly.js
- **State Management**: React Query
- **Real-Time**: Socket.io-client

### Infrastructure
- **Frontend Hosting**: Vercel
- **Backend Hosting**: Render or Railway
- **Database**: PostgreSQL (Render/Supabase)
- **File Storage**: Cloudflare R2 or Supabase Storage
- **Monitoring**: UptimeRobot, Sentry

---

## 📋 Project Structure

```
iOps/
├── backend/                    # FastAPI backend
│   ├── routers/               # API route handlers
│   ├── utils/                 # Utility functions
│   ├── middleware/            # Custom middleware
│   ├── migrations/            # Database migrations
│   ├── tests/                 # Test suite
│   ├── models.py              # SQLAlchemy models
│   ├── database.py            # Database configuration
│   ├── main.py                # FastAPI app entry point
│   └── requirements.txt        # Python dependencies
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API client
│   │   ├── contexts/          # React contexts
│   │   └── types/             # TypeScript types
│   ├── package.json           # Node dependencies
│   └── vite.config.ts         # Vite configuration
│
├── .kiro/specs/               # Feature specifications
│   └── mvp-complete-implementation/
│       ├── requirements.md    # Feature requirements
│       ├── design.md          # Technical design
│       └── tasks.md           # Implementation tasks
│
└── README.md                  # This file
```

---

## 🏁 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 12+ (or use SQLite for development)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/iOps.git
   cd iOps
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Environment Configuration**
   
   Create `backend/.env`:
   ```env
   # Database
   DATABASE_URL=sqlite:///./iops.db
   
   # API Keys
   GROQ_API_KEY=your_groq_api_key
   RESEND_API_KEY=your_resend_api_key
   
   # JWT
   SECRET_KEY=your_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRATION_MINUTES=1440
   
   # Stripe (optional for payments)
   STRIPE_SECRET_KEY=your_stripe_secret_key
   STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
   
   # Environment
   ENVIRONMENT=development
   DEBUG=true
   ```

   Create `frontend/.env`:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

### Running Locally

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Open your browser at `http://localhost:5173`

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### Run All Tests
```bash
# Backend
cd backend && pytest tests/ --cov=. --cov-report=html

# Frontend
cd frontend && npm run test:coverage
```

---

## 📚 Documentation

- **[Architecture Overview](DEPLOYMENT.md)** - System design and deployment guide
- **[Database Schema](backend/DATABASE_SCHEMA.md)** - Data model documentation
- **[API Endpoints](backend/routers/)** - REST API reference
- **[Feature Specifications](.kiro/specs/mvp-complete-implementation/)** - Detailed requirements and design

---

## 🚀 Deployment

### Deploy to Vercel (Frontend)
```bash
cd frontend
vercel deploy
```

### Deploy to Render (Backend)
1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set environment variables
4. Deploy

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

---

## 🔐 Security

- ✅ JWT authentication with 24-hour token expiration
- ✅ Bcrypt password hashing (10+ salt rounds)
- ✅ SQL injection prevention with parameterized queries
- ✅ XSS protection with input sanitization
- ✅ CSRF protection on state-changing endpoints
- ✅ Rate limiting (100 req/min per user)
- ✅ AES-256 encryption for sensitive data
- ✅ HTTPS/TLS 1.3 in production

---

## 📊 Performance

- **API Response Time**: <500ms for 95% of requests
- **Database Queries**: Indexed on frequently accessed fields
- **Frontend Bundle**: Code splitting and lazy loading
- **Caching**: 5-minute TTL on expensive queries
- **Image Optimization**: WebP format with responsive sizing

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write tests for new features
- Update documentation as needed

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/Emart29/iOpsAI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Emart29/iOpsAI/discussions)
- **Email**: nwangumaemmanuel29@gmail.com
- **LinkedIn**: [Emmanuel Nwanguma](https://linkedin.com/in/nwangumaemmanuel)

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - JavaScript UI library
- [Groq](https://groq.com/) - Fast LLM inference
- [Stripe](https://stripe.com/) - Payment processing
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework

---

<div align="center">

Made with ❤️ by [Emmanuel Nwanguma](https://linkedin.com/in/nwangumaemmanuel)

**GitHub:** [@Emart29](https://github.com/Emart29) | **Email:** nwangumaemmanuel29@gmail.com

[⬆ Back to top](#iops---ai-powered-data-science-copilot)

</div>
