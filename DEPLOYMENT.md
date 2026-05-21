# Admin Agent - CI/CD & Deployment Guide

## Overview

This project uses Docker for containerization and GitHub Actions for CI/CD automation.

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AdminAgent
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Production Deployment

1. **Build production images**
   ```bash
   docker-compose -f docker-compose.yml --profile production up -d
   ```

2. **Access via Nginx**
   - Application: http://localhost

## CI/CD Pipeline

### Workflow Stages

1. **Test Stage**
   - Backend: Python linting (ruff) + pytest
   - Frontend: ESLint + TypeScript check + build
   - Runs on every push and PR

2. **Build Stage**
   - Multi-stage Docker builds for optimization
   - Pushes images to GitHub Container Registry
   - Only on main/develop branches

3. **Deploy Stage**
   - Development: Auto-deploy on develop branch
   - Production: Auto-deploy on main branch
   - Requires environment secrets

### GitHub Actions Secrets

Configure these in your repository settings:

```
GITHUB_TOKEN (automatically provided)
OPENAI_API_KEY
SECRET_KEY
JWT_SECRET_KEY
POSTGRES_PASSWORD
```

## Docker Images

### Backend Image
- Base: `python:3.11-slim`
- Multi-stage build for smaller size
- Non-root user for security
- Health check included

### Frontend Image
- Build stage: `node:20-alpine`
- Production stage: `nginx:alpine`
- Optimized static asset serving
- Gzip compression enabled

## Testing

### Backend Tests
```bash
cd backend
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov
pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd frontend
npm install
npm run lint
npm run build
```

## Deployment Environments

### Development
- Branch: `develop`
- URL: https://dev.admin-agent.example.com
- Auto-deploy on push

### Production
- Branch: `main`
- URL: https://admin-agent.example.com
- Auto-deploy on push
- Requires manual approval (optional)

## Monitoring

### Health Checks
- Backend: `GET /health`
- Frontend: `GET /health` (nginx)
- Database: `pg_isready`
- Redis: `redis-cli ping`

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Troubleshooting

### Common Issues

1. **Database connection failed**
   ```bash
   # Check if postgres is healthy
   docker-compose ps
   # Restart postgres
   docker-compose restart postgres
   ```

2. **Port already in use**
   ```bash
   # Change ports in docker-compose.yml or .env
   # Or stop conflicting services
   ```

3. **Build cache issues**
   ```bash
   # Rebuild without cache
   docker-compose build --no-cache
   ```

## Performance Optimization

### Backend
- Uvicorn with multiple workers in production
- Database connection pooling
- Redis caching for frequent queries

### Frontend
- Vite for fast builds
- Code splitting
- Asset compression (gzip)
- CDN for static assets (recommended)

## Security Best Practices

1. **Never commit secrets**
   - Use `.env` files (gitignored)
   - Use GitHub Secrets for CI/CD

2. **Update dependencies regularly**
   ```bash
   # Backend
   pip list --outdated
   
   # Frontend
   npm outdated
   ```

3. **Use HTTPS in production**
   - Configure SSL certificates in nginx
   - Enable HSTS headers

4. **Run containers as non-root**
   - Already configured in Dockerfiles

## Backup & Recovery

### Database Backup
```bash
# Backup
docker-compose exec postgres pg_dump -U admin admin_agent > backup.sql

# Restore
docker-compose exec -T postgres psql -U admin admin_agent < backup.sql
```

### Volume Backup
```bash
# Backup volumes
docker run --rm -v admin-agent_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

## Scaling

### Horizontal Scaling
```bash
# Scale backend service
docker-compose up -d --scale backend=3

# Add load balancer (nginx) configuration
```

### Vertical Scaling
```yaml
# In docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```