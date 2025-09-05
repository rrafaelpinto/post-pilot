# Post Pilot - Multi-AI LinkedIn Content Generator

A comprehensive Django application for generating LinkedIn posts and articles using multiple AI providers. Choose between OpenAI, Grok (X.AI), and Google Gemini for content generation with asynchronous processing via Celery.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Django](https://img.shields.io/badge/Django-5.2.5-green)
![AI Providers](https://img.shields.io/badge/AI-OpenAI%20|%20Grok%20|%20Gemini-orange)
![Celery](https://img.shields.io/badge/Celery-Async-red)

## 🚀 Features

- **Multi-AI Provider Support**: OpenAI, Grok (X.AI), and Google Gemini
- **Topic Generation**: AI generates 3-5 structured topics for each theme
- **Content Creation**: Generate simple posts (up to 1300 characters) or long-form articles
- **Content Improvement**: Enhance existing posts with practical examples and secure code
- **Asynchronous Processing**: Uses Celery + Redis for non-blocking API calls
- **Complete Web Interface**: Dashboard to manage themes, posts, and view statistics
- **Markdown Rendering**: Full Markdown support in generated posts
- **Real-time Monitoring**: Flower interface to track tasks in real-time
- **Flexible Provider Switching**: Dynamic AI provider configuration

## 🤖 Supported AI Providers

| Provider | Model | Strengths | Status |
|----------|-------|-----------|--------|
| **OpenAI** | GPT-4o, GPT-4o-mini | Excellent overall quality, wide compatibility | ✅ Fully supported |
| **Grok (X.AI)** | grok-beta | Updated knowledge, created by X (Twitter) | ✅ Implemented (beta access required) |
| **Google Gemini** | gemini-1.5-pro | Good Google ecosystem integration | ✅ Implemented |

## 🛠 Technology Stack

- **Backend**: Django 5.2.5
- **AI APIs**: OpenAI, Grok (X.AI), Google Gemini
- **Queue System**: Celery + Redis
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Bootstrap 5.1.3
- **Monitoring**: Flower
- **Content**: Python-Markdown
- **Language**: 100% English interface

## 📋 Prerequisites

- Python 3.11+
- Redis Server
- At least one AI provider API key (OpenAI, Grok, or Gemini)

## 🔧 Installation & Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd post-pilot
```

### 2. Virtual Environment Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
pip install django python-dotenv openai markdown
pip install celery redis django-celery-beat flower google-generativeai
```

### 4. Environment Configuration

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

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

### 5. Redis Installation & Configuration

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

Download and install Redis from the [official repository](https://github.com/microsoftarchive/redis/releases)

### 6. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## 🚀 Running the System

### Recommended Method: Multiple Terminals

#### Terminal 1 - Django Server

```bash
python manage.py runserver
```

#### Terminal 2 - Celery Worker

```bash
./scripts/start_worker.sh
# or manually:
celery -A post_pilot worker --loglevel=info --concurrency=2 --queues=default,ai_tasks
```

#### Terminal 3 - Celery Beat (Scheduler)

```bash
./scripts/start_beat.sh
# or manually:
celery -A post_pilot beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

#### Terminal 4 - Flower (Monitoring)

```bash
./scripts/start_flower.sh
# or manually:
celery -A post_pilot flower --port=5555
```

### Access Points

- **Web Application**: <http://localhost:8000>
- **Django Admin**: <http://localhost:8000/admin>
- **Flower Monitoring**: <http://localhost:5555>

## 🤖 AI Provider Management

### Management Commands

#### List available providers

```bash
python manage.py ai_provider --list
```

#### View current provider

```bash
python manage.py ai_provider --current
```

#### Switch provider

```bash
python manage.py ai_provider --set openai   # For OpenAI
python manage.py ai_provider --set grok     # For Grok (X.AI)
python manage.py ai_provider --set gemini   # For Google Gemini
```

#### Test connection

```bash
python manage.py ai_provider --test openai
python manage.py ai_provider --test grok
python manage.py ai_provider --test gemini
```

### How to Obtain API Keys

#### OpenAI

1. Visit [platform.openai.com](https://platform.openai.com/)
2. Create an account and add payment method
3. Go to "API Keys" and create a new key
4. Add credits to your account

#### Grok (X.AI)

1. Visit [x.ai](https://x.ai/)
2. Request API access (currently in limited beta)
3. Wait for approval from X.AI team

#### Google Gemini

1. Visit [ai.google.dev](https://ai.google.dev/)
2. Create a project in Google AI Studio
3. Generate an API key
4. Free tier available with limitations

### Configuration Testing

Run the included test script:

```bash
python test_multi_ai.py
```

This will:

- Verify all configured providers
- Test API connections
- Validate topic generation
- Show configuration status

## 📖 Usage Guide

### 1. Create a Theme

1. Access the dashboard
2. Click "Create New Theme"
3. Enter theme title (e.g., "React Hooks", "Python FastAPI", "Docker")

### 2. Generate Topics

1. On the theme page, click "Generate Topics"
2. AI will create 3-5 structured topics with hooks, summaries, and CTAs
3. Processing is asynchronous - track via Flower

### 3. Create Posts

1. For each topic, choose:
   - **Simple Post**: Up to 1300 characters, optimized for LinkedIn
   - **Article**: 1000-1500 words + promotional post
2. Content is generated in Markdown format

### 4. Improve Posts

1. On the post page, click "Improve Post"
2. AI will expand content with:
   - Practical code examples
   - Detailed explanations
   - Security considerations
   - Best practices

## 🔄 Asynchronous Architecture

### Processing Flow

1. **Web Interface** → Triggers Celery task
2. **Redis** → Stores task in queue
3. **Celery Worker** → Processes AI API call
4. **Result** → Updates database
5. **Interface** → Shows result or status

### Configured Queues

- `default`: General tasks
- `ai_tasks`: Specific AI calls (isolated)

### Retry Strategy

- **Maximum**: 3 attempts
- **Delay**: Progressive (60s, 120s, 180s)
- **Timeout**: 10 minutes per task

## 📊 Monitoring with Flower

Access <http://localhost:5555> to:

- View running tasks
- Monitor queues and workers
- See execution history
- Monitor performance

## 🔧 Advanced Configuration

### AI Models Used by Provider

#### OpenAI

- **Topics**: GPT-4o-mini (economical and fast)
- **Simple Posts**: GPT-4o-mini
- **Articles**: GPT-4o (higher quality)
- **Improvements**: GPT-4o (better analysis)

#### Grok

- **All operations**: grok-beta

#### Gemini

- **All operations**: gemini-1.5-pro

### Performance Settings

```python
# settings.py
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_SOFT_TIME_LIMIT = 300  # 5 minutes
CELERY_TASK_TIME_LIMIT = 600       # 10 minutes
```

## 🐛 Troubleshooting

### Redis Connection Issues

```bash
# Check if Redis is running
redis-cli ping  # Should return "PONG"

# Check port
sudo netstat -tlnp | grep :6379
```

### Celery Worker Won't Start

```bash
# Check logs
celery -A post_pilot worker --loglevel=debug

# Verify settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.CELERY_BROKER_URL)
```

### AI API Timeout

```bash
# Verify API Key
python manage.py shell
>>> import os
>>> print(os.getenv('OPENAI_API_KEY'))
```

### Provider Switching Issues

```bash
# Restart Celery workers after changing provider
celery -A post_pilot worker --reload
```

## 📝 Data Structure

### Theme Model

- `title`: Theme title
- `suggested_topics`: AI-generated topics (JSON)
- `processing_status`: Async processing status
- `is_active`: Active status

### Post Model

- `post_type`: 'simple' or 'article'
- `content`: Content in Markdown
- `promotional_post`: Promotional post (articles only)
- `processing_status`: Async processing status
- `ai_model_used`: AI model used for generation

## 🚀 Production Deployment

### Recommended Settings

```bash
# PostgreSQL
pip install psycopg2-binary

# Gunicorn
pip install gunicorn

# Supervisor for process management
sudo apt install supervisor
```

### Environment Variables for Production

```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/postpilot
CELERY_BROKER_URL=redis://localhost:6379/0
```

### Docker Compose Example

```yaml
version: '3.8'
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: postpilot
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
  
  web:
    build: .
    command: gunicorn post_pilot.wsgi:application --bind 0.0.0.0:8000
    depends_on:
      - db
      - redis
  
  worker:
    build: .
    command: celery -A post_pilot worker --loglevel=info
    depends_on:
      - db
      - redis
```

## 🔒 Security Considerations

- Keep API keys secure in environment variables
- Use HTTPS in production
- Implement rate limiting for AI API calls
- Monitor API usage and costs
- Regular security updates for dependencies

## 💰 Cost Optimization

### OpenAI

- Use GPT-4o-mini for cost-effective operations
- Implement caching for repeated requests
- Monitor token usage

### Grok

- Pricing to be announced (currently in beta)

### Gemini

- Utilize free tier limits effectively
- Monitor rate limits

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the project
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 🆘 Support

For questions and support:

- Open an issue on GitHub
- Check Django documentation
- Review Celery documentation
- Consult AI provider documentation

## 🏗 Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │────│   Django Views  │────│     Models      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Celery Tasks   │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ AI Service      │
                       │ Factory         │
                       └─────────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
            ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
            │   OpenAI    │ │    Grok     │ │   Gemini    │
            │   Service   │ │   Service   │ │   Service   │
            └─────────────┘ └─────────────┘ └─────────────┘
```

## 📈 Version History

- **v2.0.0**: Multi-AI provider support, full English translation
- **v1.5.0**: Celery integration, asynchronous processing
- **v1.0.0**: Initial release with OpenAI support

---

**Developed with ❤️ for optimizing technical content creation on LinkedIn**
