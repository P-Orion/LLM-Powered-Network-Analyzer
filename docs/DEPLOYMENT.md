# Deployment Guide

This guide covers different deployment scenarios for the LLM-Powered Network Analyzer.

## 🎯 Deployment Options

### 1. Local Development (Default)
- **Use case**: Development, testing, personal use
- **Requirements**: Local machine with Python, Node.js, Ollama
- **Setup**: Follow main README.md instructions

### 2. Local Production
- **Use case**: Single-user production environment
- **Requirements**: Dedicated machine or VM
- **Benefits**: Better performance, isolated environment

### 3. Docker Deployment
- **Use case**: Containerized deployment
- **Requirements**: Docker and Docker Compose
- **Benefits**: Consistent environment, easy deployment

### 4. Enterprise Deployment
- **Use case**: Multiple users, enterprise environment
- **Requirements**: Server infrastructure, load balancing
- **Benefits**: Scalability, centralized management

## 🐳 Docker Deployment

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 16GB+ RAM (for Gemma 2 12B model)
- 50GB+ disk space

### Docker Setup

#### 1. Create Dockerfile for Backend

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start script
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
```

#### 2. Create Backend Start Script

Create `backend/start.sh`:
```bash
#!/bin/bash

# Start Ollama in background
ollama serve &

# Wait for Ollama to be ready
sleep 10

# Pull Gemma model if not exists
ollama pull gemma2:12b

# Start FastAPI application
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 3. Create Dockerfile for Frontend

Create `frontend/Dockerfile`:
```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist/network-analyzer /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### 4. Create Nginx Configuration

Create `frontend/nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        # Handle Angular routing
        location / {
            try_files $uri $uri/ /index.html;
        }

        # Proxy API requests to backend
        location /api/ {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # Proxy WebSocket connections
        location /ws/ {
            proxy_pass http://backend:8000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }
    }
}
```

#### 5. Create Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: network-analyzer-backend
    ports:
      - "8000:8000"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    container_name: network-analyzer-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  ollama_data:
```

#### 6. Deploy with Docker Compose

```bash
# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🏢 Enterprise Deployment

### Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Web Server    │    │   Application   │
│    (nginx)      │────│    (nginx)      │────│    Servers      │
│                 │    │                 │    │   (multiple)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                               ┌─────────────────┐
                                               │   Ollama/LLM    │
                                               │    Servers      │
                                               │   (dedicated)   │
                                               └─────────────────┘
```

### Requirements

#### Hardware Requirements
- **Application Servers**: 8+ CPU cores, 32GB+ RAM, 100GB+ SSD
- **LLM Servers**: 16+ CPU cores, 64GB+ RAM, 500GB+ SSD
- **Load Balancer**: 4+ CPU cores, 16GB+ RAM, 50GB+ SSD

#### Software Requirements
- **OS**: Ubuntu 22.04 LTS or RHEL 8+
- **Container Runtime**: Docker 20.10+ or Podman
- **Orchestration**: Kubernetes 1.25+ (optional)
- **Monitoring**: Prometheus, Grafana
- **Logging**: ELK Stack or similar

### Kubernetes Deployment

#### 1. Create Namespace

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: network-analyzer
```

#### 2. Backend Deployment

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: network-analyzer
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: network-analyzer/backend:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        env:
        - name: OLLAMA_HOST
          value: "ollama-service"
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: network-analyzer
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

#### 3. Ollama Deployment

```yaml
# ollama-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
  namespace: network-analyzer
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ollama
  template:
    metadata:
      labels:
        app: ollama
    spec:
      containers:
      - name: ollama
        image: ollama/ollama:latest
        ports:
        - containerPort: 11434
        resources:
          requests:
            memory: "16Gi"
            cpu: "4"
          limits:
            memory: "32Gi"
            cpu: "8"
        volumeMounts:
        - name: ollama-data
          mountPath: /root/.ollama
      volumes:
      - name: ollama-data
        persistentVolumeClaim:
          claimName: ollama-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: ollama-service
  namespace: network-analyzer
spec:
  selector:
    app: ollama
  ports:
  - port: 11434
    targetPort: 11434
  type: ClusterIP
```

#### 4. Frontend Deployment

```yaml
# frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: network-analyzer
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: network-analyzer/frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "512Mi"
            cpu: "0.5"
          limits:
            memory: "1Gi"
            cpu: "1"
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: network-analyzer
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
  type: LoadBalancer
```

#### 5. Deploy to Kubernetes

```bash
# Apply configurations
kubectl apply -f namespace.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f ollama-deployment.yaml
kubectl apply -f frontend-deployment.yaml

# Check status
kubectl get pods -n network-analyzer
kubectl get services -n network-analyzer

# Scale if needed
kubectl scale deployment backend --replicas=5 -n network-analyzer
```

## 🔒 Security Considerations

### Network Security
- **Firewall**: Only expose necessary ports (80, 443)
- **TLS/SSL**: Use HTTPS in production
- **VPN**: Consider VPN access for enterprise deployment
- **Network Segmentation**: Isolate application network

### Application Security
- **Authentication**: Implement user authentication
- **Authorization**: Role-based access control
- **Input Validation**: Validate all uploaded files
- **Rate Limiting**: Prevent abuse and DoS attacks

### Data Security
- **Encryption**: Encrypt data at rest and in transit
- **Backup**: Regular backups of configuration and data
- **Audit Logging**: Log all user actions
- **Data Retention**: Implement data retention policies

### Example Security Configuration

#### 1. TLS/SSL with Let's Encrypt

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 2. Rate Limiting

```nginx
http {
    limit_req_zone $binary_remote_addr zone=upload:10m rate=1r/s;
    
    server {
        location /api/upload {
            limit_req zone=upload burst=5 nodelay;
            proxy_pass http://backend:8000;
        }
    }
}
```

## 📊 Monitoring and Logging

### Health Checks

#### Backend Health Check
```python
# Add to backend/main.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "ollama_status": check_ollama_health()
    }
```

#### Monitoring with Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'network-analyzer'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: /metrics
```

### Logging Configuration

#### Structured Logging
```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName
        }
        return json.dumps(log_entry)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/network-analyzer.log')
    ]
)
```

## 🚀 Performance Optimization

### Backend Optimization
- **Async Processing**: Use async/await for I/O operations
- **Connection Pooling**: Pool database connections
- **Caching**: Cache frequently accessed data
- **Load Balancing**: Distribute load across multiple instances

### Frontend Optimization
- **Lazy Loading**: Load components on demand
- **Bundle Optimization**: Minimize bundle size
- **CDN**: Use CDN for static assets
- **Compression**: Enable gzip compression

### LLM Optimization
- **Model Caching**: Keep models in memory
- **Batch Processing**: Process multiple requests together
- **GPU Acceleration**: Use GPU for inference if available
- **Model Quantization**: Use quantized models for better performance

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] All tests pass
- [ ] Security review completed
- [ ] Performance testing done
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Documentation updated

### Deployment
- [ ] Infrastructure provisioned
- [ ] Applications deployed
- [ ] Health checks passing
- [ ] SSL certificates configured
- [ ] DNS configured
- [ ] Load balancer configured

### Post-Deployment
- [ ] Smoke tests completed
- [ ] Monitoring alerts configured
- [ ] Log aggregation working
- [ ] Backup verification
- [ ] Performance baseline established
- [ ] Team training completed

## 🆘 Troubleshooting Deployment Issues

### Common Issues
- **Out of Memory**: Increase memory allocation for Ollama
- **Slow Performance**: Check CPU/memory usage, optimize queries
- **Connection Timeouts**: Increase timeout values
- **SSL Issues**: Verify certificate configuration

### Debug Commands
```bash
# Check container logs
docker logs network-analyzer-backend
docker logs network-analyzer-frontend

# Check resource usage
docker stats

# Test connectivity
curl -f http://localhost:8000/health
curl -f http://localhost/api/health

# Check Ollama
docker exec -it network-analyzer-backend ollama list
```

---

For more deployment assistance, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or create a [GitHub issue](https://github.com/P-Orion/LLM-Powered-Network-Analyzer/issues).