"""
EmailTriage OpenEnv — Python Client
===================================
Wraps the HTTP API as an async Python class.
Mirrors the openenv client interface: reset() / step() / state() / close()

Usage:
    from email_triage_env import EmailTriageEnv, EmailTriageAction

    env = EmailTriageEnv(base_url="http://localhost:7860", task="inbox-triage")
    result = await env.reset()
    result = await env.step(EmailTriageAction(category="work", priority=2))
    await env.close()
"""

import asyncio
import subprocess
import time
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel


# ─────────────────────────────────────────────────────────────────────────────
# Action / Observation models (mirrors server-side types)
# ─────────────────────────────────────────────────────────────────────────────

class EmailTriageAction(BaseModel):
    """
    Agent's decision for a single email.
    category:        spam | work | personal | newsletter | important | social
    priority:        1 (critical) → 5 (ignore)
    respond:         True if the agent wants to draft a reply
    response_draft:  The reply text (scored only for tasks that include response_weight)
    unsubscribe:     True if the agent wants to unsubscribe from this sender
    """
    category: str
    priority: int
    respond: bool = False
    response_draft: Optional[str] = None
    unsubscribe: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# Lightweight wrappers for API response fields
# ─────────────────────────────────────────────────────────────────────────────

class _Email:
    def __init__(self, data: Optional[Dict]) -> None:
        if data is None:
            self._data: Dict = {}
            self.id = self.sender = self.sender_email = ""
            self.subject = self.body = self.timestamp = ""
            self.has_attachment = False
            return
        self._data = data
        self.id            = data.get("id", "")
        self.sender        = data.get("sender", "")
        self.sender_email  = data.get("sender_email", "")
        self.subject       = data.get("subject", "")
        self.body          = data.get("body", "")
        self.timestamp     = data.get("timestamp", "")
        self.has_attachment = data.get("has_attachment", False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Email id={self.id!r} subject={self.subject[:40]!r}>"


class _Observation:
    def __init__(self, data: Dict) -> None:
        self._data           = data
        self.current_email   = _Email(data.get("current_email"))
        self.emails_remaining = data.get("emails_remaining", 0)
        self.emails_processed = data.get("emails_processed", 0)
        self.total_emails    = data.get("total_emails", 0)
        self.episode_reward  = data.get("episode_reward", 0.0)
        self.step            = data.get("step", 0)
        self.task_name       = data.get("task_name", "")
        self.context         = data.get("context", {})


class _StepResult:
    def __init__(self, data: Dict) -> None:
        self._data      = data
        self.observation = _Observation(data.get("observation", {}))
        self.reward      = data.get("reward", 0.0)
        self.done        = data.get("done", False)
        self.info        = data.get("info", {})


# ─────────────────────────────────────────────────────────────────────────────
# Client
# ─────────────────────────────────────────────────────────────────────────────

class EmailTriageEnv:
    """
    Async client for the EmailTriage OpenEnv server.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:7860",
        task: str = "categorize-single",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.task = task
        self._client = httpx.AsyncClient(timeout=60.0)
        self._container_id: Optional[str] = None

    # ── Factory: spin up from Docker image ────────────────────────────────────

    @classmethod
    async def from_docker_image(
        cls,
        image_name: str,
        task: str = "categorize-single",
        host_port: int = 7860,
        wait_seconds: int = 30,
    ) -> "EmailTriageEnv":
        """
        Pull and start the Docker container, then wait for it to be healthy.
        """
        print(f"[DEBUG] Starting container from image: {image_name}", flush=True)
        proc = subprocess.Popen(
            ["docker", "run", "-d", "-p", f"{host_port}:7860", image_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"docker run failed: {stderr.decode()}")

        container_id = stdout.decode().strip()
        print(f"[DEBUG] Container started: {container_id[:12]}", flush=True)

        env = cls(base_url=f"http://localhost:{host_port}", task=task)
        env._container_id = container_id

        # Poll /health until ready
        for _ in range(wait_seconds):
            try:
                async with httpx.AsyncClient(timeout=2.0) as probe:
                    r = await probe.get(f"http://localhost:{host_port}/health")
                    if r.status_code == 200:
                        print("[DEBUG] Server is healthy.", flush=True)
                        return env
            except Exception:
                pass
            await asyncio.sleep(1)

        raise RuntimeError(f"Server did not become healthy within {wait_seconds}s")

    # ── OpenEnv API ───────────────────────────────────────────────────────────

    async def reset(self, task: Optional[str] = None) -> _StepResult:
        task = task or self.task
        r = await self._client.post(
            f"{self.base_url}/reset",
            json={"task": task},
        )
        r.raise_for_status()
        return _StepResult(r.json())

    async def step(self, action: EmailTriageAction) -> _StepResult:
        r = await self._client.post(
            f"{self.base_url}/step",
            json=action.model_dump(),
        )
        r.raise_for_status()
        return _StepResult(r.json())

    async def state(self) -> Dict[str, Any]:
        r = await self._client.get(f"{self.base_url}/state")
        r.raise_for_status()
        return r.json()

    async def close(self) -> None:
        await self._client.aclose()
        if self._container_id:
            try:
                subprocess.run(
                    ["docker", "stop", self._container_id],
                    check=True, capture_output=True,
                )
                print(f"[DEBUG] Container {self._container_id[:12]} stopped.", flush=True)
            except Exception as e:
                print(f"[DEBUG] Could not stop container: {e}", flush=True)
