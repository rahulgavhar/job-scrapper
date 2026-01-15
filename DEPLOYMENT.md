# Deployment Guide

## Local Development

### Prerequisites
- Python 3.11+
- pip

### Setup

```bash
# Clone repository
cd job-scrapper

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access at: `http://localhost:8000`

---

## Docker Deployment

### Build & Run

```bash
# Build Docker image
docker build -t job-recommendation-api:latest .

# Run container
docker run -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  job-recommendation-api:latest
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Dockerfile

For production, use the provided Dockerfile which includes:
- Multi-stage build for smaller image size
- Health checks
- Non-root user execution (recommended)

---

## Cloud Deployment

### AWS (Elastic Container Service)

1. **Build and push image to ECR**
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <your-ecr-uri>
docker tag job-recommendation-api:latest <ecr-uri>/job-recommendation-api:latest
docker push <ecr-uri>/job-recommendation-api:latest
```

2. **Create ECS task definition**
```json
{
  "family": "job-recommendation-api",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "<ecr-uri>/job-recommendation-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "memory": 1024,
      "cpu": 512,
      "essential": true,
      "environment": [
        {
          "name": "APP_ENV",
          "value": "production"
        }
      ]
    }
  ]
}
```

3. **Create ECS service and launch**

### Heroku

1. **Create Procfile**
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

2. **Create .env file for Heroku**
```bash
heroku create job-recommendation-api
heroku config:set PYTHONUNBUFFERED=1
git push heroku main
```

### Google Cloud Run

1. **Ensure Dockerfile exists** ✓ (provided)

2. **Deploy to Cloud Run**
```bash
gcloud run deploy job-recommendation-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000
```

### Azure App Service

1. **Create Web App**
```bash
az webapp up \
  --name job-recommendation-api \
  --resource-group myResourceGroup \
  --runtime "PYTHON|3.11"
```

2. **Set startup command**
```bash
az webapp config appsettings set \
  -g myResourceGroup \
  -n job-recommendation-api \
  --settings STARTUP_COMMAND="uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

### DigitalOcean App Platform

1. **Create app.yaml**
```yaml
name: job-recommendation-api
services:
- name: api
  source:
    type: github
    repo: your-username/job-scrapper
    branch: main
  http_port: 8000
  health_check:
    http_path: /health
  envs:
  - key: APP_ENV
    value: production
```

2. **Deploy**
```bash
doctl apps create --spec app.yaml
```

---

## Production Checklist

### Security
- [ ] Set `DEBUG=False` in .env
- [ ] Add rate limiting middleware
- [ ] Implement API key authentication
- [ ] Use HTTPS/TLS
- [ ] Add CORS restrictions (not `"*"`)
- [ ] Validate file uploads
- [ ] Sanitize user inputs

### Performance
- [ ] Add Redis caching for recommendations
- [ ] Implement job result caching
- [ ] Use async processing for PDF uploads
- [ ] Add database indexing
- [ ] Implement pagination limits
- [ ] Add request timeouts

### Monitoring & Logging
- [ ] Set up centralized logging (ELK, Splunk)
- [ ] Add application monitoring (New Relic, DataDog)
- [ ] Set up error tracking (Sentry)
- [ ] Create health check endpoints
- [ ] Add metrics/telemetry

### Database
- [ ] Migrate from fake_db to PostgreSQL/MongoDB
- [ ] Set up database backups
- [ ] Add database connection pooling
- [ ] Create database indexes

### Infrastructure
- [ ] Set up load balancing
- [ ] Configure auto-scaling
- [ ] Set up CDN for static files
- [ ] Implement disaster recovery plan
- [ ] Set up monitoring/alerting

---

## Environment Variables

### Development
```env
DEBUG=True
API_PORT=8000
```

### Production
```env
DEBUG=False
API_PORT=8000
ENABLE_JOB_SCRAPING=True
MIN_MATCH_SCORE=0.5
```

---

## Scaling Considerations

### Horizontal Scaling
- Deploy multiple instances behind load balancer
- Use managed container orchestration (Kubernetes, ECS)
- Implement cache invalidation strategy

### Vertical Scaling
- Increase container CPU/memory
- Use larger instance types
- Optimize code for performance

### Database Scaling
- Implement read replicas
- Use connection pooling
- Shard data if needed

---

## SSL/TLS Certificate

### Using Let's Encrypt with Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Backup & Recovery

### Database Backups
```bash
# PostgreSQL backup
pg_dump dbname > backup.sql

# Restore
psql dbname < backup.sql
```

### File Uploads Backup
```bash
tar czf uploads_backup.tar.gz uploads/
```

---

## Monitoring & Alerts

### Key Metrics to Monitor
- API response time
- Error rate
- PDF processing time
- Skill extraction accuracy
- Job matching performance
- Database query time
- Memory usage
- CPU usage

### Alert Thresholds
- Response time > 5s: Alert
- Error rate > 1%: Alert
- CPU usage > 80%: Alert
- Memory usage > 85%: Alert

---

## CI/CD Pipeline Example (GitHub Actions)

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Build Docker image
      run: docker build -t job-recommendation-api:${{ github.sha }} .
    
    - name: Push to registry
      run: docker push job-recommendation-api:${{ github.sha }}
    
    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy job-recommendation-api \
          --image=job-recommendation-api:${{ github.sha }} \
          --platform managed \
          --region us-central1
```

---

## Troubleshooting

### Container won't start
```bash
docker logs <container-id>
```

### Port already in use
```bash
lsof -i :8000  # Find process
kill -9 <pid>  # Kill process
```

### Out of memory
- Increase container memory allocation
- Optimize PDF processing
- Implement result caching

### High latency
- Check network connectivity
- Monitor database performance
- Profile application code

---

## Support & Documentation

- API Docs: `/api/docs`
- Swagger UI: `/api/docs` (interactive)
- OpenAPI Schema: `/api/openapi.json`
- Health Check: `/health`

