# 🐳 Docker Development Setup

## Quick Start with Docker Compose

### 1. Development Environment (Recommended)

```bash
# Start all services in development mode
docker-compose -f docker-compose.dev.yml up --build

# Or run in background
docker-compose -f docker-compose.dev.yml up -d --build

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

### 2. Production-like Environment

```bash
# Start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build

# Stop services
docker-compose down
```

## Services

After starting with docker-compose, you can access:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432

## Environment Setup

1. Copy environment variables:
```bash
cp .env.example .env
```

2. Edit `.env` file with your settings if needed

## Database Initialization

The database will be automatically initialized when you start the services for the first time.

If you need to reset the database:
```bash
# Stop services
docker-compose -f docker-compose.dev.yml down

# Remove database volume
docker volume rm pneumonia-app_postgres_dev_data

# Start services again
docker-compose -f docker-compose.dev.yml up --build
```

## Individual Service Management

### Backend Only
```bash
# Start only database and backend
docker-compose -f docker-compose.dev.yml up db backend
```

### Frontend Only
```bash
# Start only frontend (backend must be running)
docker-compose -f docker-compose.dev.yml up frontend
```

## Development Tips

1. **Hot Reload**: Both frontend and backend support hot reload
2. **Code Changes**: Changes to your code will automatically reflect in the containers
3. **Debugging**: Use `docker-compose logs -f [service-name]` to view logs
4. **Health Checks**: Services have health checks to ensure proper startup order

## Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :3000  # or :8000, :5432

# Kill the process
kill -9 [PID]
```

### Database Connection Issues
```bash
# Check database logs
docker-compose -f docker-compose.dev.yml logs db

# Restart database
docker-compose -f docker-compose.dev.yml restart db
```

### Clear Everything and Start Fresh
```bash
# Stop and remove all containers, networks, and volumes
docker-compose -f docker-compose.dev.yml down -v

# Remove all images
docker-compose -f docker-compose.dev.yml down --rmi all

# Start fresh
docker-compose -f docker-compose.dev.yml up --build
```
