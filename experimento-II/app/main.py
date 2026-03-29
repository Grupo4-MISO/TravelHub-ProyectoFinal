from fastapi import FastAPI, Response, status
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="k8s-observability-experiment", version="1.0.0")
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

state = {"forced_unhealthy": False}


@app.get("/")
def root() -> dict:
    return {
        "service": "k8s-observability-experiment",
        "status": "running",
        "forced_unhealthy": state["forced_unhealthy"],
    }


@app.get("/health")
def health(response: Response) -> dict:
    if state["forced_unhealthy"]:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "unhealthy",
            "reason": "forced by /simulate/down endpoint",
        }

    return {"status": "healthy"}


@app.post("/simulate/down")
def simulate_down() -> dict:
    state["forced_unhealthy"] = True
    return {
        "message": "Application marked as unhealthy. /health now returns 503.",
        "forced_unhealthy": state["forced_unhealthy"],
    }


@app.post("/simulate/up")
def simulate_up() -> dict:
    state["forced_unhealthy"] = False
    return {
        "message": "Application marked as healthy. /health now returns 200.",
        "forced_unhealthy": state["forced_unhealthy"],
    }
