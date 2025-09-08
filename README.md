# Post Pilot - Multi-AI LinkedIn Content Generator

A modern full-stack application for generating LinkedIn posts and articles using multiple AI providers. Built with React TypeScript frontend and Django REST Framework backend, featuring OpenAI, Grok (X.AI), and Google Gemini integration with asynchronous processing.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Django](https://img.shields.io/badge/Django-5.2.5-green)
![React](https://img.shields.io/badge/React-19.1.1-61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-4.9.5-blue)
![AI Providers](https://img.shields.io/badge/AI-OpenAI%20|%20Grok%20|%20Gemini-orange)
![Celery](https://img.shields.io/badge/Celery-Async-red)

## 🚀 Features

- **Modern Full-Stack Architecture**: React TypeScript frontend + Django REST Framework backend
- **Multi-AI Provider Support**: OpenAI, Grok (X.AI), and Google Gemini
- **Topic Generation**: AI generates 3-5 structured topics for each theme
- **Content Creation**: Generate simple posts (up to 1300 characters) or long-form articles
- **Content Improvement**: Enhance existing posts with practical examples and secure code
- **Real-time Updates**: Asynchronous processing with live status updates
- **RESTful API**: Complete REST API with Django REST Framework
- **Responsive UI**: Modern React interface with Bootstrap components
- **Type Safety**: Full TypeScript implementation for better developer experience
- **Monitoring**: Flower interface to track background tasks

## 🤖 Supported AI Providers

| Provider | Model | Strengths | Status |
|----------|-------|-----------|--------|
| **OpenAI** | GPT-4o, GPT-4o-mini | Excellent overall quality, wide compatibility | ✅ Fully supported |
| **Grok (X.AI)** | grok-beta | Updated knowledge, created by X (Twitter) | ✅ Implemented (beta access required) |
| **Google Gemini** | gemini-1.5-pro | Good Google ecosystem integration | ✅ Implemented |

## 🛠 Technology Stack

### Frontend

- **React 19.1.1** - Modern UI library
- **TypeScript 4.9.5** - Type safety and better DX
- **React Router DOM 7.8.2** - Client-side routing
- **Bootstrap 5.3.8** + **React Bootstrap 2.10.10** - UI components
- **Axios 1.11.0** - HTTP client for API communication
- **React Markdown 10.1.0** - Markdown rendering

### Backend

- **Django 5.2.5** - Web framework
- **Django REST Framework 3.15.2** - REST API toolkit
- **django-cors-headers 4.7.0** - CORS handling
- **Celery 5.5.3** + **Redis** - Asynchronous task processing
- **SQLite** (development) / **PostgreSQL** (production)
- **Flower 2.0.1** - Celery monitoring
- **Multiple AI SDKs** - OpenAI, Grok, Gemini integration

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 16+** and **npm**
- **Redis Server**
- At least one AI provider API key (OpenAI, Grok, or Gemini)

## 🔧 Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/rrafaelpinto/post-pilot
cd post-pilot
```

### 2. Backend Setup (Django REST Framework)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

### 3. Frontend Setup (React TypeScript)

```bash
cd ../frontend
npm install
```

### 4. Environment Configuration

Create environment files for both backend and frontend:

#### Backend (.env)

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env`:

```env
# AI Providers Configuration
DEFAULT_AI_PROVIDER=openai  # openai, grok, gemini

# OpenAI Configuration (required if using openai)
OPENAI_API_KEY=sk-your_openai_key_here

# Grok (X.AI) Configuration (required if using grok)
GROK_API_KEY=xai-your_grok_key_here

# Google Gemini Configuration (required if using gemini)
GEMINI_API_KEY=your_gemini_key_here

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Django Configuration
DEBUG=True
SECRET_KEY=your_secret_key_here
```

#### Frontend (.env)

```bash
cd frontend
```

Create `frontend/.env`:

```env
REACT_APP_API_BASE_URL=http://localhost:8000
```

### 5. Redis Installation

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### macOS (Homebrew)

```bash
brew install redis
brew services start redis
```

#### Windows

Download Redis from [official repository](https://github.com/microsoftarchive/redis/releases)

### 6. Database Setup

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## 🚀 Running the Application

### Quick Start with Scripts

```bash
# Terminal 1 - Backend Django REST API
./start_backend.sh         # http://localhost:8000

# Terminal 2 - Frontend React App  
./start_frontend.sh         # http://localhost:3000

# Terminal 3 - Celery Worker (for AI tasks)
./start_celery.sh          # Background processing
```

### Manual Start

#### Backend Django REST API

```bash
cd backend
source .venv/bin/activate
python manage.py runserver
```

#### Frontend React Application

```bash
cd frontend
npm start
```

#### Celery Worker (Optional for AI tasks)

```bash
cd backend
source .venv/bin/activate
celery -A post_pilot worker --loglevel=info
```

#### Celery Beat Scheduler (Optional)

```bash
cd backend
source .venv/bin/activate
celery -A post_pilot beat --loglevel=info
```

#### Flower Monitoring (Optional)

```bash
cd backend
source .venv/bin/activate
celery -A post_pilot flower
```

## 🌐 Application URLs

- **React Frontend**: <http://localhost:3000>
- **Django API**: <http://localhost:8000/api/>
- **Django Admin**: <http://localhost:8000/admin/>
- **API Browser**: <http://localhost:8000/api/> (DRF Browsable API)
- **Flower Monitoring**: <http://localhost:5555>

## 📁 Project Structure

```
post-pilot/
├── 📁 backend/              # Django REST Framework API
│   ├── 📁 core/            # Main Django app
│   │   ├── models.py       # Theme and Post models
│   │   ├── serializers.py  # DRF serializers
│   │   ├── api_views.py    # API ViewSets
│   │   ├── api_urls.py     # API URL patterns
│   │   ├── services.py     # AI service implementations
│   │   ├── tasks.py        # Celery tasks
│   │   └── admin.py        # Django admin
│   ├── 📁 post_pilot/      # Django project settings
│   │   ├── settings.py     # Main settings
│   │   ├── urls.py         # Main URL configuration
│   │   └── celery.py       # Celery configuration
│   ├── 📁 scripts/         # Automation scripts
│   ├── manage.py           # Django CLI
│   └── requirements.txt    # Python dependencies
│
├── 📁 frontend/             # React TypeScript Application
│   ├── 📁 src/
│   │   ├── 📁 components/  # React components
│   │   ├── 📁 pages/       # Page components
│   │   ├── 📁 hooks/       # Custom React hooks
│   │   ├── 📁 services/    # API client services
│   │   ├── 📁 types/       # TypeScript type definitions
│   │   └── App.tsx         # Main App component
│   ├── package.json        # Node.js dependencies
│   └── tsconfig.json       # TypeScript configuration
│
├── start_backend.sh         # Backend startup script
├── start_frontend.sh        # Frontend startup script
├── start_celery.sh         # Celery startup script
└── README.md               # Project documentation
```

## 🔌 API Endpoints

### Dashboard

- `GET /api/dashboard/stats/` - Dashboard statistics

### Themes

- `GET /api/themes/` - List themes
- `POST /api/themes/` - Create theme
- `GET /api/themes/{id}/` - Theme details
- `POST /api/themes/{id}/generate_topics/` - Generate topics
- `POST /api/themes/{id}/generate_post/` - Generate post
- `GET /api/themes/{id}/posts/` - Theme posts
- `GET /api/themes/{id}/status/` - Processing status

### Posts

- `GET /api/posts/` - List posts
- `GET /api/posts/{id}/` - Post details
- `PATCH /api/posts/{id}/` - Update post
- `POST /api/posts/{id}/improve/` - Improve post content
- `POST /api/posts/{id}/regenerate_image_prompt/` - Regenerate image prompt
- `POST /api/posts/{id}/publish/` - Publish post
- `GET /api/posts/{id}/status/` - Processing status

### Tasks

- `GET /api/tasks/check/?task_id={id}` - Check Celery task status

## 🤖 AI Provider Management

### Switching AI Providers

You can switch between AI providers using Django management commands:

```bash
cd backend
python manage.py ai_provider --set openai   # For OpenAI
python manage.py ai_provider --set grok     # For Grok (X.AI)
python manage.py ai_provider --set gemini   # For Google Gemini
```

### Testing AI Providers

```bash
# Test specific provider
python manage.py ai_provider --test openai
python manage.py ai_provider --test grok
python manage.py ai_provider --test gemini

# List available providers
python manage.py ai_provider --list

# View current provider
python manage.py ai_provider --current
```

### How to Obtain API Keys

#### OpenAI

1. Visit [platform.openai.com](https://platform.openai.com/)
2. Create account and add payment method
3. Generate API key in "API Keys" section
4. Add credits to your account

#### Grok (X.AI)

1. Visit [x.ai](https://x.ai/)
2. Request API access (currently in limited beta)
3. Wait for approval from X.AI team

#### Google Gemini

1. Visit [ai.google.dev](https://ai.google.dev/)
2. Create project in Google AI Studio
3. Generate API key
4. Free tier available with limitations

## 📖 Usage Guide

### 1. Access the Application

1. Start the backend: `./start_backend.sh`
2. Start the frontend: `./start_frontend.sh`
3. Open <http://localhost:3000> in your browser

### 2. Create a Theme

1. Navigate to the dashboard
2. Click "Create New Theme"
3. Enter theme title (e.g., "React Hooks", "Python FastAPI", "Docker")

### 3. Generate Topics

1. On the theme page, click "Generate Topics"
2. AI will create 3-5 structured topics with hooks, summaries, and CTAs
3. Processing is asynchronous - status updates in real-time

### 4. Create Posts

1. For each topic, choose:
   - **Simple Post**: Up to 1300 characters, optimized for LinkedIn
   - **Article**: 1000-1500 words + promotional post
2. Content is generated in Markdown format

### 5. Improve Posts

1. On the post page, click "Improve Post"
2. AI will expand content with:
   - Practical code examples
   - Detailed explanations
   - Security considerations
   - Best practices

## 🔄 Architecture Overview

### Frontend Architecture

```
React App (TypeScript)
├── Components (React Bootstrap)
├── Pages (Route Components)
├── Hooks (Custom React Hooks)
├── Services (API Client)
└── Types (TypeScript Definitions)
```

### Backend Architecture

```
Django REST Framework
├── Models (Database Layer)
├── Serializers (Data Validation)
├── ViewSets (API Endpoints)
├── Services (AI Integrations)
└── Tasks (Celery Background Jobs)
```

### Communication Flow

```
React Frontend → Axios → Django REST API → Celery Tasks → AI Providers
     ↑                                           ↓
     └─── Real-time Polling ←─── Task Status ←──┘
```

## 🔧 Development Features

### Real-time Updates

- **Task Polling**: Custom React hooks monitor background tasks
- **Live Status**: Real-time updates for AI generation progress
- **Auto-refresh**: Automatic UI updates when tasks complete

### Type Safety

- **Full TypeScript**: Complete type coverage in frontend
- **API Types**: Strongly typed API responses
- **DRF Serializers**: Backend validation and type checking

### Error Handling

- **React Error Boundaries**: Graceful error handling
- **API Error Responses**: Structured error messages
- **Retry Logic**: Automatic retry for failed AI requests

## 🚀 Production Deployment

### Frontend Deployment

```bash
cd frontend
npm run build
# Deploy build/ directory to static hosting (Netlify, Vercel, etc.)
```

### Backend Deployment

```bash
# Use production settings
export DJANGO_SETTINGS_MODULE=post_pilot.settings.production

# Install production dependencies
pip install gunicorn psycopg2-binary

# Collect static files
python manage.py collectstatic

# Run with Gunicorn
gunicorn post_pilot.wsgi:application --bind 0.0.0.0:8000
```

### Environment Variables for Production

```env
# Backend
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/postpilot
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Frontend
REACT_APP_API_BASE_URL=https://api.yourdomain.com
```

## 🐛 Troubleshooting

### Common Issues

#### Frontend not connecting to backend

```bash
# Check REACT_APP_API_BASE_URL in frontend/.env
echo $REACT_APP_API_BASE_URL

# Verify CORS settings in backend
python manage.py shell
>>> from django.conf import settings
>>> print(settings.CORS_ALLOWED_ORIGINS)
```

#### Redis connection issues

```bash
# Test Redis connection
redis-cli ping  # Should return "PONG"

# Check if Redis is running
sudo systemctl status redis-server
```

#### Celery tasks not running

```bash
# Check Celery worker status
celery -A post_pilot inspect active

# Restart Celery worker
./start_celery.sh
```

#### TypeScript compilation errors

```bash
cd frontend
npm run build  # Check for TypeScript errors
```

## 📊 Monitoring

### Development Monitoring

- **React DevTools**: Component debugging
- **Django Debug Toolbar**: SQL query analysis
- **Flower**: Celery task monitoring at <http://localhost:5555>

### Production Monitoring

- **Application logs**: Configure proper logging
- **Performance monitoring**: Use tools like Sentry
- **Database monitoring**: Monitor query performance
- **Task queue monitoring**: Monitor Celery performance

## 🔒 Security Best Practices

### Development

- Keep API keys in environment variables
- Use HTTPS in production
- Implement proper CORS settings
- Regular dependency updates

### Production

- Use secure secret keys
- Implement rate limiting
- Monitor API usage and costs
- Regular security audits

## 📚 API Documentation

The API is fully documented using Django REST Framework's browsable API. Visit <http://localhost:8000/api/> to explore all available endpoints with interactive documentation.

### Key Features

- **Interactive API Browser**: Test endpoints directly
- **Request/Response Examples**: See expected data formats
- **Authentication Info**: API key requirements
- **Schema Documentation**: Complete API schema

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Setup for Contributors

```bash
# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate

# Frontend setup
cd ../frontend
npm install
npm start

# Run tests
cd ../backend
python manage.py test
cd ../frontend
npm test
```

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🆘 Support

- **Issues**: Open an issue on GitHub
- **Documentation**: Check the API documentation at `/api/`
- **Community**: Join discussions in GitHub Discussions

---

**Built with ❤️ for modern LinkedIn content creation**
