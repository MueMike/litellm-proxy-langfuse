# Deployment Guide

This guide covers different deployment scenarios for the LiteLLM Proxy with LangFuse integration.

## Table of Contents
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Cloud Deployments](#cloud-deployments)

## Local Development

### Prerequisites
- Python 3.11+
- pip
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/MueMike/litellm-proxy-langfuse.git
cd litellm-proxy-langfuse
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. **Run the server**
```bash
python main.py
```

The server will be available at:
- API: http://localhost:8000
- Metrics: http://localhost:9090

## Docker Deployment

### Prerequisites
- Docker
- Docker Compose

### Quick Start

1. **Clone and configure**
```bash
git clone https://github.com/MueMike/litellm-proxy-langfuse.git
cd litellm-proxy-langfuse
cp .env.example .env
# Edit .env with your configuration
```

2. **Start services**
```bash
cd docker
docker-compose up -d
```

3. **View logs**
```bash
docker-compose logs -f litellm-proxy
```

4. **Stop services**
```bash
docker-compose down
```

### Custom Configuration

To customize the Docker deployment:

1. **Edit docker-compose.yml** for:
   - Port mappings
   - Resource limits
   - Volume mounts
   - Environment variables

2. **Rebuild after changes**
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

## Production Deployment

### Security Checklist

- [ ] Set `REQUIRE_AUTH=true`
- [ ] Configure `LITELLM_MASTER_KEY` with a strong key
- [ ] Use HTTPS/TLS termination (reverse proxy)
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerting
- [ ] Configure log aggregation
- [ ] Use secrets management (not .env files)
- [ ] Set appropriate resource limits
- [ ] Enable health checks

### Recommended Architecture

```
Internet
    │
    ▼
Load Balancer (HTTPS)
    │
    ├─▶ LiteLLM Proxy Instance 1
    ├─▶ LiteLLM Proxy Instance 2
    └─▶ LiteLLM Proxy Instance 3
         │
         ├─▶ LangFuse (Existing)
         └─▶ Prometheus/Grafana
```

### Environment Variables for Production

```bash
# Security
REQUIRE_AUTH=true
LITELLM_MASTER_KEY=your-secure-key-here

# Monitoring
ENABLE_PROMETHEUS=true
ENABLE_REQUEST_LOGGING=true
LOG_LEVEL=INFO

# Performance
MAX_RETRIES=3
REQUEST_TIMEOUT=600
ENABLE_RATE_LIMITING=true
RATE_LIMIT_RPM=100

# LangFuse
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=from-secrets-manager
LANGFUSE_SECRET_KEY=from-secrets-manager
LANGFUSE_HOST=https://your-langfuse-instance.com
```

### Reverse Proxy Configuration

#### Nginx Example

```nginx
upstream litellm_proxy {
    server localhost:8000;
    # Add more servers for load balancing
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://litellm_proxy;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running requests
        proxy_read_timeout 600s;
        proxy_connect_timeout 60s;
        proxy_send_timeout 600s;
    }
}
```

## Cloud Deployments

### AWS ECS/Fargate

1. **Build and push Docker image**
```bash
docker build -f docker/Dockerfile -t your-ecr-repo/litellm-proxy:latest .
docker push your-ecr-repo/litellm-proxy:latest
```

2. **Create ECS Task Definition**
- Use Fargate launch type
- Configure environment variables from Secrets Manager
- Set appropriate CPU/memory (2 vCPU, 4GB RAM recommended)
- Configure health check endpoint: `/health`

3. **Create ECS Service**
- Enable auto-scaling (target CPU 70%)
- Configure Application Load Balancer
- Set min instances: 2, max instances: 10

### Google Cloud Run

1. **Build and deploy**
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/litellm-proxy
gcloud run deploy litellm-proxy \
  --image gcr.io/PROJECT-ID/litellm-proxy \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 600 \
  --set-env-vars LANGFUSE_HOST=https://...,PROXY_PORT=8080
```

### Azure Container Instances

1. **Create container group**
```bash
az container create \
  --resource-group myResourceGroup \
  --name litellm-proxy \
  --image your-acr.azurecr.io/litellm-proxy:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8000 9090 \
  --environment-variables \
    PROXY_PORT=8000 \
    LANGFUSE_HOST=https://... \
  --secure-environment-variables \
    LANGFUSE_PUBLIC_KEY=... \
    LANGFUSE_SECRET_KEY=... \
    OPENAI_API_KEY=...
```

### Kubernetes

1. **Create deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: litellm-proxy
spec:
  replicas: 3
  selector:
    matchLabels:
      app: litellm-proxy
  template:
    metadata:
      labels:
        app: litellm-proxy
    spec:
      containers:
      - name: litellm-proxy
        image: your-registry/litellm-proxy:latest
        ports:
        - containerPort: 8000
        - containerPort: 9090
        env:
        - name: LANGFUSE_PUBLIC_KEY
          valueFrom:
            secretKeyRef:
              name: litellm-secrets
              key: langfuse-public-key
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

## Monitoring Setup

### Prometheus

Add scrape config:
```yaml
scrape_configs:
  - job_name: 'litellm-proxy'
    static_configs:
      - targets: ['localhost:9090']
```

### Grafana Dashboard

Import the provided Grafana dashboard or create custom panels for:
- Request rate by model
- Error rate
- Latency percentiles (p50, p95, p99)
- Token usage
- Cost tracking

### LangFuse Dashboard

Access your LangFuse instance to view:
- Trace details
- Session analytics
- Cost breakdown
- User activity
- Custom metadata

## Troubleshooting

### Health Check Failures

1. Check logs: `docker-compose logs litellm-proxy`
2. Verify environment variables
3. Test health endpoint: `curl http://localhost:8000/health`

### Connection Issues

1. Verify network configuration
2. Check firewall rules
3. Verify API keys are correct
4. Check LangFuse connectivity

### Performance Issues

1. Increase resource limits
2. Enable caching
3. Adjust rate limits
4. Scale horizontally

## Backup and Recovery

### Configuration Backup
```bash
# Backup .env and config files
tar -czf config-backup-$(date +%Y%m%d).tar.gz .env config/
```

### LangFuse Data
- Configure regular backups through LangFuse
- Export traces periodically

## Scaling Recommendations

| Load Level | Instances | CPU/Instance | Memory/Instance |
|------------|-----------|--------------|-----------------|
| Light      | 1-2       | 1 vCPU       | 2 GB           |
| Medium     | 2-4       | 2 vCPU       | 4 GB           |
| Heavy      | 4-10      | 2 vCPU       | 4 GB           |
| Very Heavy | 10+       | 4 vCPU       | 8 GB           |

## Support

For deployment issues:
- Check [Troubleshooting Guide](README.md#troubleshooting)
- Open an issue on GitHub
- Review logs for error details
