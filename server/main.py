"""
EmailTriage OpenEnv — FastAPI server
Exposes: POST /reset, POST /step, GET /state, GET /health, GET /tasks
"""

from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import Action, ResetRequest, StepResult, StateResult
from .env import get_env
from .tasks import TASK_CONFIGS

app = FastAPI(
    title="EmailTriage OpenEnv",
    description=(
        "Real-world email triage environment for training and evaluating AI agents. "
        "Implements the full OpenEnv spec: reset / step / state API with typed Pydantic models."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "env": "email-triage-env", "version": "1.0.0"}


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "name": "EmailTriage OpenEnv",
        "version": "1.0.0",
        "tasks": list(TASK_CONFIGS.keys()),
        "endpoints": {
            "reset": "POST /reset",
            "step":  "POST /step",
            "state": "GET  /state",
        },
    }


@app.get("/tasks")
async def list_tasks() -> Dict[str, Any]:
    return {
        name: {
            "display_name": cfg["display_name"],
            "difficulty":   cfg["difficulty"],
            "description":  cfg["description"],
            "max_steps":    cfg["max_steps"],
        }
        for name, cfg in TASK_CONFIGS.items()
    }


@app.post("/reset", response_model=StepResult)
async def reset(request: Optional[ResetRequest] = None) -> StepResult:
    """
    Start a new episode. Body is optional — defaults to task=categorize-single.
    """
    if request is None:
        request = ResetRequest()
    env = get_env()
    try:
        result = env.reset(task_name=request.task)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


@app.post("/step", response_model=StepResult)
async def step(action: Action) -> StepResult:
    """
    Submit an action for the current email.
    """
    env = get_env()
    try:
        result = env.step(action)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return result


@app.get("/state", response_model=StateResult)
async def state() -> StateResult:
    env = get_env()
    return env.state()
