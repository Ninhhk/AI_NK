# Deployment Assets

- Kubernetes manifest archived from k8s/ai-nvcb-deployment.yaml.
- Note: Health probes in the manifest use legacy paths (`/health/live`, `/health/ready`). Current API mounts health endpoints under `/api`.

Use containers built via uv-driven Dockerfile. For production, prefer docker-compose.prod.yml.