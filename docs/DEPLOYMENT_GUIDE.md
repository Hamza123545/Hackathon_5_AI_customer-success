# Customer Success FTE - Deployment Guide

## Prerequisites

- **Kubernetes Cluster** (Minikube, EKS, GKE, or AKS)
- **kubectl** CLI installed and configured
- **Docker** (for building images)
- **PostgreSQL Client** (optional, for debugging)

## 1. Build Docker Images

```bash
cd backend
docker build -t fte-backend:latest .
# If using Minikube, load image:
# minikube image load fte-backend:latest
```

## 2. Kubernetes Configuration

### Create Namespace
```bash
kubectl apply -f backend/k8s/namespace.yaml
```

### Configure Secrets
**IMPORTANT**: Edit `backend/k8s/secrets.yaml` with your actual API keys before applying.
```bash
cp backend/k8s/secrets.yaml backend/k8s/secrets-prod.yaml
# Edit secrets-prod.yaml
kubectl apply -f backend/k8s/secrets-prod.yaml
```

### Apply Configurations
```bash
kubectl apply -f backend/k8s/configmap.yaml
```

## 3. Deploy Infrastructure

### Database (PostgreSQL)
```bash
kubectl apply -f backend/k8s/postgres-statefulset.yaml
```

### Metrics Server (For HPA)
```bash
kubectl apply -f backend/k8s/metrics-service.yaml
```

## 4. Deploy Application

### API Service
```bash
kubectl apply -f backend/k8s/deployment-api.yaml
kubectl apply -f backend/k8s/service.yaml
kubectl apply -f backend/k8s/hpa-api.yaml
```

### Worker Service
```bash
kubectl apply -f backend/k8s/deployment-worker.yaml
kubectl apply -f backend/k8s/hpa-worker.yaml
```

### Ingress (Optional)
```bash
kubectl apply -f backend/k8s/ingress.yaml
```

## 5. Verify Deployment

```bash
# Check Pods
kubectl get pods -n fte-namespace

# Check Logs
kubectl logs -f deployment/fte-api -n fte-namespace
kubectl logs -f deployment/fte-message-processor -n fte-namespace
```

## Troubleshooting

- **CrashLoopBackOff**: Check logs `kubectl logs <pod-name> -n fte-namespace`. Often due to missing env vars or DB connection issues.
- **Pending**: Check PVC status `kubectl get pvc -n fte-namespace`.
- **HPA not scaling**: Verify Metrics Server is running `kubectl get pods -n kube-system`.
