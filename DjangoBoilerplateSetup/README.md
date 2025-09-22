# Django Boilerplate Template

Production-ready Django project template with JWT authentication, standardized API responses, Docker setup, and security features. Use this template to quickly create new Django projects with best practices built-in.

## Features

### Core Framework
- Django 5.0
- Django REST Framework
- JWT Authentication
- PostgreSQL
- Redis
- Celery

### Security & Monitoring
- Django Defender
- Content Security Policy
- Permissions Policy
- CORS Headers
- Request Correlation IDs
- Sentry Integration

### API Features
- Standardized Responses
- Automatic Documentation
- Request Throttling
- Pagination
- Custom Exception Handling

### Development & Deployment
- Docker Setup
- Environment Configuration
- Code Quality Tools
- Static File Handling
- Structured Logging

### Utilities
- Custom User Model
- Audit Trail System
- Email Setup
- File Upload Handling
- Data Import/Export

## Prerequisites

- Docker and Docker Compose Installation

## Quick Start - Create New Project

### Automated Setup (Recommended)
Create a new Django project using this boilerplate template, replace MyNewProject with your project name:

**Option 1: From GitHub (Recommended)**
```bash
django-admin startproject MyNewProject \
  --extension py,json,yml,yaml,toml \
  --name Dockerfile,README.md,.env.example,.gitignore,Makefile \
  --template=https://github.com/saksham-shil/Django-Boilerplate-Setup/archive/refs/heads/main.zip
```

**Option 2: From Local Path**
```bash
# If you have cloned this repository locally
django-admin startproject MyNewProject \
  --extension py,json,yml,yaml,toml \
  --name Dockerfile,README.md,.env.example,.gitignore,Makefile \
  --template=/path/to/DjangoBoilerplateSetup
```

Replace `MyNewProject` with your desired project name and update the template URL to point to your repository.

**What gets automatically updated:**
- Django project name and directory structure
- Database names in docker-compose.yml
- All Django settings references (ROOT_URLCONF, WSGI_APPLICATION, etc.)
- Celery app name
- Poetry project name
- Environment variable templates
- Volume names in Docker setup

### Setup Steps After Project Creation

1. **Navigate to your project:**
```bash
cd MyNewProject
```

2. **Create environment file:**
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your specific configuration
```

3. **Start development environment:**
```bash
make docker_setup
docker compose up -d
make docker_migrate
make docker_createsuperuser
```

4. **Access your application:**
- API Documentation: http://localhost:8000/api/schema/swagger-ui/
- Admin Interface: http://localhost:8000/admin/
- API Endpoints: http://localhost:8000/api/

### Manual Setup (If django-admin template doesn't work)

If you need to set up manually or customize further:

1. **Clone and rename:**
```bash
git clone <this-repo-url> MyNewProject
cd MyNewProject
rm -rf .git
git init
```

2. **Update project references manually:**
- Rename `backend/{{ project_name }}/` directory to `backend/MyNewProject/`
- Update all `{{ project_name }}` placeholders with `MyNewProject`
- Update `{{ secret_key }}` in `.env` with a generated Django secret key

3. **Follow steps 2-4 from Automated Setup above**

## Environment Variables

The template includes a `backend/.env.example` file with all required variables. Copy it to create your `.env` file:

```bash
cp backend/.env.example backend/.env
```

Key variables to update in your `.env` file:

```env
# Django Settings
DJANGO_SETTINGS_MODULE=YourProjectName.settings.local
DEBUG=True
SECRET_KEY=your-generated-secret-key-here

# Database
DATABASE_URL=postgres://YourProjectName:password@db:5432/YourProjectName

# Redis & Celery
REDIS_URL=redis://result:6379/0
CELERY_BROKER_URL=amqp://broker:5672//

# Security
ALLOWED_HOSTS=localhost,127.0.0.1,backend
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173

# API Configuration
BASE_URL=http://127.0.0.1:8000
REST_FRAMEWORK_PAGE_SIZE=10

# JWT Configuration
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=30
JWT_REFRESH_TOKEN_LIFETIME_DAYS=14

# Rate Limiting
THROTTLE_ANON=100/hour
THROTTLE_USER=2000/day
THROTTLE_BURST=60/min

# Email Settings
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
EMAIL_TIMEOUT=20

# Security Features
DEFENDER_LOGIN_FAILURE_LIMIT=3
DEFENDER_COOLOFF_TIME=300

# Admin User
ADMIN_NAME=Admin
ADMIN_EMAIL=admin@example.com

# Optional
SENTRY_DSN=
FRONTEND_DOMAIN=localhost:3000
AUTO_APPROVE_USERS=True
```

## Docker Commands

### Setup Commands
```bash
make docker_setup          # Initial setup with volume creation
make docker_up             # Start all services
make docker_down           # Stop all services
```

### Development Commands
```bash
make docker_migrate         # Run database migrations
make docker_makemigrations  # Create new migrations
make docker_shell           # Access Django shell
make docker_backend_shell   # Access backend container shell
```

### Testing & Quality
```bash
make docker_test           # Run tests
make test                  # Run tests locally with Poetry
```

### Maintenance
```bash
make docker_collectstatic  # Collect static files
make docker_createsuperuser # Create Django superuser
make clean                 # Clean Python cache files
```

## Project Structure

```
DjangoBoilerplateSetup/
├── backend/
│   ├── DjangoBoilerplateSetup/     # Django project settings
│   │   ├── settings/               # Environment-specific settings
│   │   │   ├── base.py            # Common settings
│   │   │   ├── local.py           # Development settings
│   │   │   ├── production.py      # Production settings
│   │   │   └── test.py            # Test settings
│   │   ├── urls.py                # Main URL configuration
│   │   └── wsgi.py                # WSGI configuration
│   ├── apps/
│   │   ├── common/                # Shared utilities
│   │   │   ├── api_responses/     # Standardized API responses
│   │   │   ├── audit/             # Audit trail system
│   │   │   ├── base_views/        # Base view classes
│   │   │   ├── email/             # Email utilities
│   │   │   ├── pagination.py      # Custom pagination
│   │   │   └── utils.py           # Helper functions
│   │   └── users/                 # User management
│   ├── templates/                 # Django templates
│   ├── logs/                      # Application logs
│   ├── mediafiles/               # User uploaded files
│   └── .env                      # Environment variables
├── docker-compose.yml            # Docker services configuration
├── pyproject.toml               # Python dependencies
├── Makefile                     # Development commands
└── README.md                    # This file
```

## Security Features

### Authentication & Authorization
- JWT token-based authentication
- Configurable token lifetimes
- User role management
- Login attempt protection

### Request Security
- CORS configuration
- CSRF protection
- Content Security Policy
- Permissions Policy headers
- Request correlation IDs

### Rate Limiting
- Anonymous user throttling
- Authenticated user limits
- Burst protection
- Configurable rate limits

## API Documentation

- Swagger UI: `/api/schema/swagger-ui/`
- ReDoc: `/api/schema/redoc/`
- OpenAPI Schema: `/api/schema/`

## Testing

```bash
# Using Docker
make docker_test

# Using Poetry (local)
make test

# With coverage
docker compose run --rm backend coverage run --source='.' manage.py test
docker compose run --rm backend coverage report
```

## Logging

- API Requests: `logs/api_requests.log`
- API Errors: `logs/api_errors.log`
- General Django: `logs/django.log`
- Console Output: For development

## Production Deployment

### Environment Variables for Production
```env
DEBUG=False
DJANGO_SETTINGS_MODULE=MyNewProject.settings.production
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com
SENTRY_DSN=your-sentry-dsn
```

### Static Files
```bash
make docker_collectstatic
```

### Database Backup
```bash
docker compose exec db pg_dump -U MyNewProject MyNewProject > backup.sql
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

If you encounter issues:

1. Check the logs: `docker compose logs backend`
2. Verify environment variables in `.env`
3. Ensure all services are running: `docker compose ps`
4. Check the Django admin for user management

## Updates

To update dependencies:
```bash
poetry update
docker compose build --no-cache
```