# Experimento Kubernetes + Observabilidad (Python)

Proyecto mínimo para probar probes de Kubernetes y herramientas de observación (Prometheus/New Relic).

## Endpoints

- `GET /health`
  - Retorna `200` cuando la app está saludable.
  - Retorna `503` cuando se fuerza indisponibilidad.
- `POST /simulate/down`
  - Fuerza estado no saludable (`/health` => `503`).
- `POST /simulate/up`
  - Restaura estado saludable (`/health` => `200`).
- `GET /metrics`
  - Métricas en formato Prometheus.
- `GET /`
  - Estado general de la aplicación.

## Ejecutar local

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Pruebas rápidas:

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/simulate/down
curl http://localhost:8000/health
curl -X POST http://localhost:8000/simulate/up
curl http://localhost:8000/metrics
```

## Docker

```bash
docker build -t k8s-observability-experiment:latest .
docker run --rm -p 8000:8000 k8s-observability-experiment:latest
```

## Ejemplo de probes en Kubernetes

En tu `Deployment`, usa:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 3
  periodSeconds: 5
```

Si llamas `POST /simulate/down`, Kubernetes debería marcar el pod como no listo (y eventualmente reiniciarlo según política/probe).


## Configuración del experimento

A continuación, se va a explicar la forma en la que se configura y ejecutar el experimento propuesto

### Pre-requisitos
- Kubernetes(EKS, Minikube, K3S)
- Kubectl
- Helm