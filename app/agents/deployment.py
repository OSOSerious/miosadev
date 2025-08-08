from app.agents.base import BaseAgent
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)

class DeploymentAgent(BaseAgent):
    """
    Deployment Agent - Handles deployment and DevOps tasks
    """
    
    def __init__(self):
        super().__init__("deployment", "devops_specialist")
        
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type", "prepare_deployment")
        
        if task_type == "prepare_deployment":
            return await self._prepare_deployment(task)
        elif task_type == "generate_docker":
            return await self._generate_docker(task)
        elif task_type == "generate_kubernetes":
            return await self._generate_kubernetes(task)
        elif task_type == "generate_cicd":
            return await self._generate_cicd(task)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _prepare_deployment(self, task: Dict) -> Dict:
        components = task.get("components", {})
        requirements = task.get("requirements", {})
        
        deployment_files = {}
        
        deployment_files["docker"] = await self._generate_docker_files(components)
        
        deployment_files["kubernetes"] = await self._generate_kubernetes_manifests(components)
        
        deployment_files["cicd"] = await self._generate_cicd_pipeline(components, requirements)
        
        deployment_files["infrastructure"] = await self._generate_infrastructure_code(requirements)
        
        deployment_files["monitoring"] = await self._generate_monitoring_config(components)
        
        deployment_files["scripts"] = await self._generate_deployment_scripts(components)
        
        return {
            "deployment_files": deployment_files,
            "environment_config": await self._generate_environment_config(components),
            "deployment_guide": await self._generate_deployment_guide(components, requirements),
            "estimated_costs": await self._estimate_deployment_costs(requirements)
        }
    
    async def _generate_docker_files(self, components: Dict) -> Dict[str, str]:
        files = {}
        
        if "backend" in components:
            files["backend/Dockerfile"] = await self._generate_backend_dockerfile(
                components["backend"]
            )
        
        if "frontend" in components:
            files["frontend/Dockerfile"] = await self._generate_frontend_dockerfile(
                components["frontend"]
            )
        
        files["docker-compose.yml"] = await self._generate_docker_compose(components)
        
        files[".dockerignore"] = """
node_modules
.env
.git
*.log
dist
build
.vscode
.idea
__pycache__
*.pyc
.pytest_cache
coverage
.coverage
"""
        
        return files
    
    async def _generate_backend_dockerfile(self, backend: Dict) -> str:
        framework = backend.get("framework", "fastapi")
        
        if framework == "fastapi":
            return """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        else:
            return f"# Dockerfile for {framework}"
    
    async def _generate_frontend_dockerfile(self, frontend: Dict) -> str:
        framework = frontend.get("framework", "react")
        
        return """FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \\
    CMD wget --no-verbose --tries=1 --spider http://localhost || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
"""
    
    async def _generate_docker_compose(self, components: Dict) -> str:
        services = []
        
        services.append("""  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER:?missing}
      POSTGRES_PASSWORD: ${DB_PASSWORD:?missing}
      POSTGRES_DB: ${DB_NAME:?missing}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser"]
      interval: 10s
      timeout: 5s
      retries: 5""")
        
        if "backend" in components:
            services.append("""  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: ${DATABASE_URL:?missing}
      JWT_SECRET: ${JWT_SECRET:?missing}
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000""")
        
        if "frontend" in components:
            services.append("""  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      VITE_API_URL: ${API_URL:-http://localhost:8000}
    depends_on:
      - backend""")
        
        return f"""version: '3.8'

services:
{chr(10).join(services)}

volumes:
  postgres_data:

networks:
  default:
    name: app_network
"""
    
    async def _generate_kubernetes_manifests(self, components: Dict) -> Dict[str, str]:
        manifests = {}
        
        manifests["namespace.yaml"] = """apiVersion: v1
kind: Namespace
metadata:
  name: miosa-app
"""
        
        manifests["configmap.yaml"] = """apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: miosa-app
data:
  API_URL: "http://backend-service:8000"
  FRONTEND_URL: "http://frontend-service:3000"
"""
        
        if "backend" in components:
            manifests["backend-deployment.yaml"] = await self._generate_k8s_deployment("backend", components["backend"])
            manifests["backend-service.yaml"] = await self._generate_k8s_service("backend")
        
        if "frontend" in components:
            manifests["frontend-deployment.yaml"] = await self._generate_k8s_deployment("frontend", components["frontend"])
            manifests["frontend-service.yaml"] = await self._generate_k8s_service("frontend")
        
        manifests["ingress.yaml"] = await self._generate_k8s_ingress(components)
        
        return manifests
    
    async def _generate_k8s_deployment(self, name: str, component: Dict) -> str:
        return f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}-deployment
  namespace: miosa-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {name}
  template:
    metadata:
      labels:
        app: {name}
    spec:
      containers:
      - name: {name}
        image: {name}:latest
        ports:
        - containerPort: {8000 if name == 'backend' else 80}
        envFrom:
        - configMapRef:
            name: app-config
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
"""
    
    async def _generate_k8s_service(self, name: str) -> str:
        port = 8000 if name == "backend" else 80
        return f"""apiVersion: v1
kind: Service
metadata:
  name: {name}-service
  namespace: miosa-app
spec:
  selector:
    app: {name}
  ports:
  - protocol: TCP
    port: {port}
    targetPort: {port}
  type: ClusterIP
"""
    
    async def _generate_k8s_ingress(self, components: Dict) -> str:
        return """apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  namespace: miosa-app
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
"""
    
    async def _generate_cicd_pipeline(self, components: Dict, requirements: Dict) -> Dict[str, str]:
        pipelines = {}
        
        pipelines[".github/workflows/ci.yml"] = """name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push Docker images
        run: |
          docker build -t ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-backend:latest ./backend
          docker push ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-backend:latest
          
          docker build -t ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-frontend:latest ./frontend
          docker push ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-frontend:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Deploy to production
        run: |
          echo "Deploying to production..."
          # Add deployment commands here
"""
        
        pipelines[".gitlab-ci.yml"] = """stages:
  - test
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: ""

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r backend/requirements.txt
    - pip install pytest pytest-cov
    - cd backend && pytest tests/ --cov=app

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA ./backend
    - docker build -t $CI_REGISTRY_IMAGE/frontend:$CI_COMMIT_SHA ./frontend
    - docker push $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE/frontend:$CI_COMMIT_SHA

deploy:
  stage: deploy
  only:
    - main
  script:
    - echo "Deploying to production..."
"""
        
        return pipelines
    
    async def _generate_infrastructure_code(self, requirements: Dict) -> Dict[str, str]:
        return {
            "terraform/main.tf": await self._generate_terraform(requirements),
            "ansible/playbook.yml": await self._generate_ansible_playbook()
        }
    
    async def _generate_terraform(self, requirements: Dict) -> str:
        return """terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default = "us-west-2"
}

resource "aws_ecs_cluster" "main" {
  name = "miosa-cluster"
}

resource "aws_ecs_service" "app" {
  name            = "miosa-app"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 3
}
"""
    
    async def _generate_ansible_playbook(self) -> str:
        return """---
- name: Deploy MIOSA Application
  hosts: production
  become: yes
  
  tasks:
    - name: Install Docker
      apt:
        name: docker.io
        state: present
    
    - name: Start Docker service
      service:
        name: docker
        state: started
        enabled: yes
    
    - name: Pull latest images
      docker_image:
        name: "{{ item }}"
        source: pull
      loop:
        - backend:latest
        - frontend:latest
    
    - name: Run docker-compose
      docker_compose:
        project_src: /opt/miosa
        state: present
"""
    
    async def _generate_monitoring_config(self, components: Dict) -> Dict[str, str]:
        return {
            "prometheus.yml": """global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
  
  - job_name: 'frontend'
    static_configs:
      - targets: ['frontend:3000']
""",
            "grafana-dashboard.json": "{}",  # Simplified
            "alerts.yml": """groups:
  - name: app_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: High error rate detected
"""
        }
    
    async def _generate_deployment_scripts(self, components: Dict) -> Dict[str, str]:
        return {
            "deploy.sh": """#!/bin/bash
set -e

echo "Starting deployment..."

# Build images
docker-compose build

# Run database migrations
docker-compose run backend python -m alembic upgrade head

# Start services
docker-compose up -d

echo "Deployment complete!"
""",
            "rollback.sh": """#!/bin/bash
set -e

echo "Starting rollback..."

# Stop current deployment
docker-compose down

# Restore previous version
docker-compose pull
docker-compose up -d

echo "Rollback complete!"
"""
        }
    
    async def _generate_environment_config(self, components: Dict) -> Dict:
        return {
            ".env.example": """# Database (required in production)
DB_HOST=
DB_PORT=5432
DB_USER=
DB_PASSWORD=
DB_NAME=

# Application (generate a strong random secret in production)
JWT_SECRET=
API_URL=
FRONTEND_URL=

# External Services
REDIS_URL=
""",
            "production.env": "# Production environment variables",
            "staging.env": "# Staging environment variables"
        }
    
    async def _generate_deployment_guide(self, components: Dict, requirements: Dict) -> str:
        return """# Deployment Guide

## Prerequisites
- Docker and Docker Compose installed
- Kubernetes cluster (for K8s deployment)
- PostgreSQL database

## Local Development
1. Copy `.env.example` to `.env` and configure
2. Run `docker-compose up -d`
3. Access the application at http://localhost:3000

## Production Deployment

### Using Docker Compose
1. Configure production environment variables
2. Run `./deploy.sh`

### Using Kubernetes
1. Apply manifests: `kubectl apply -f k8s/`
2. Configure ingress for your domain

## Monitoring
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Rollback
Run `./rollback.sh` to restore previous version
"""
    
    async def _estimate_deployment_costs(self, requirements: Dict) -> Dict:
        base_cost = 100  # Base monthly cost
        
        if requirements.get("scale") == "high":
            base_cost *= 3
        
        return {
            "estimated_monthly_cost": f"${base_cost}",
            "breakdown": {
                "compute": f"${base_cost * 0.6}",
                "storage": f"${base_cost * 0.2}",
                "network": f"${base_cost * 0.2}"
            }
        }
    
    async def _generate_docker(self, task: Dict) -> Dict:
        components = task.get("components", {})
        return await self._generate_docker_files(components)
    
    async def _generate_kubernetes(self, task: Dict) -> Dict:
        components = task.get("components", {})
        return await self._generate_kubernetes_manifests(components)
    
    async def _generate_cicd(self, task: Dict) -> Dict:
        components = task.get("components", {})
        requirements = task.get("requirements", {})
        return await self._generate_cicd_pipeline(components, requirements)