# TalentAI Pro - Production Deployment Guide

> **Last Updated:** 2026-04-22

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Docker | 20.10+ | [Install Guide](https://docs.docker.com/get-docker/) |
| Docker Compose | 2.0+ | [Install Guide](https://docs.docker.com/compose/install/) |
| Git | 2.0+ | For cloning the repository |

## Quick Start (Development)

```bash
# Clone and setup
git clone https://github.com/your-org/TalentAI-Pro.git
cd TalentAI-Pro

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Start server
python run_server.py
```

## Production Deployment

### 1. Server Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Disk | 20 GB | 50+ GB SSD |
| OS | Ubuntu 20.04 | Ubuntu 22.04 LTS |

### 2. Clone Repository

```bash
ssh user@your-server
git clone https://github.com/your-org/TalentAI-Pro.git
cd TalentAI-Pro
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Required settings:**

```env
# Generate a secure key
API_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Database
DATABASE_URL=postgresql://talentai:YOUR_SECURE_PASSWORD@localhost:5432/talentai

# Feishu (optional)
FEISHU_APP_ID=your-app-id
FEISHU_APP_SECRET=your-app-secret

# Bitable (optional)
BITABLE_APP_ID=your-app-id
BITABLE_APP_SECRET=your-app-secret
```

### 4. Deploy with Docker Compose

```bash
# Linux/Mac
chmod +x scripts/deploy.sh
./scripts/deploy.sh production

# Windows
scripts\deploy.bat production
```

### 5. Verify Deployment

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f api

# Test health endpoint
curl http://localhost:8000/health
```

### 6. SSL Configuration (Recommended)

```bash
# Create SSL directory
mkdir -p ssl

# Copy your SSL certificates
cp your-cert.pem ssl/cert.pem
cp your-key.pem ssl/key.pem

# Uncomment SSL lines in nginx.conf
# ssl_certificate /etc/nginx/ssl/cert.pem;
# ssl_certificate_key /etc/nginx/ssl/key.pem;
```

## Docker Compose Services

| Service | Port | Description |
|---------|------|-------------|
| `api` | 8000 | TalentAI Pro API server |
| `db` | 5432 | PostgreSQL database |
| `redis` | 6379 | Redis cache |
| `nginx` | 80/443 | Reverse proxy |

## Data Persistence

All persistent data is stored in Docker volumes:

```
postgres-data  → PostgreSQL data
redis-data    → Redis data
./data        → Application data files
./logs        → Application logs
```

**Important:** These volumes persist across container restarts. To completely reset:

```bash
docker-compose down -v  # WARNING: This deletes all data
```

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
# Response: {"status": "healthy", "timestamp": "..."}
```

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f db
```

### Stats

```bash
# Container resource usage
docker stats

# Container processes
docker-compose ps
```

## Backup & Restore

### Backup Database

```bash
# Create backup
docker-compose exec db pg_dump -U talentai talentai > backup_$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T db psql -U talentai talentai < backup_20260422.sql
```

### Backup Volumes

```bash
# Backup PostgreSQL
docker run --rm -v talentai-postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data

# Backup Redis
docker run --rm -v talentai-redis-data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup.tar.gz /data
```

## Scaling

### Horizontal Scaling (Multiple API Instances)

```yaml
# docker-compose.override.yml
api:
  deploy:
    replicas: 3
  depends_on:
    - db
    - redis
  environment:
    - DATABASE_URL=postgresql://talentai:password@db:5432/talentai
    - REDIS_URL=redis://redis:6379/0
```

Apply with:
```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

## Security Checklist

- [ ] Change default database password
- [ ] Enable SSL/TLS
- [ ] Set `DEBUG=false`
- [ ] Configure firewall (only expose 80/443)
- [ ] Regular security updates: `docker-compose pull`
- [ ] Enable authentication on all endpoints
- [ ] Rotate API keys periodically

## Troubleshooting

### API Container Won't Start

```bash
# Check logs
docker-compose logs api

# Common issues:
# - Port 8000 already in use: change port mapping
# - Database connection failed: check DATABASE_URL
# - Missing environment variables: verify .env file
```

### Database Connection Error

```bash
# Check if database is ready
docker-compose exec db pg_isready -U talentai

# Check connection string
docker-compose exec api env | grep DATABASE
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Increase resources in docker-compose.yml
```

## Updating

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose build --pull
docker-compose up -d

# Run migrations if needed
docker-compose exec api python -m alembic upgrade head
```

## Uninstall

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```
