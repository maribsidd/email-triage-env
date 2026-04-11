"""
run_local.py — quick local smoke test (no Docker, no API key needed)
Starts the server in-process and runs a dummy agent through all 3 tasks.
"""

import asyncio
import json
import urllib.request
import subprocess
import time
import sys
import os


BASE = "http://127.0.0.1:7863"

TASK_ANSWERS = {
    "categorize-single": [
        {"category": "spam",       "priority": 5, "respond": False, "response_draft": None, "unsubscribe": False},
        {"category": "work",       "priority": 3, "respond": False, "response_draft": None, "unsubscribe": False},
        {"category": "personal",   "priority": 3, "respond": False, "response_draft": None, "unsubscribe": False},
        {"category": "newsletter", "priority": 4, "respond": False, "response_draft": None, "unsubscribe": False},
        {"category": "important",  "priority": 2, "respond": False, "response_draft": None, "unsubscribe": False},
    ],
    "inbox-triage": [
        {"category": "work",       "priority": 1, "respond": False, "response_draft": None, "unsubscribe": False},
        {"category": "work",       "priority": 2, "respond": False, "response_draft": None, "unsubscribe": False},
        {"category": "important",  "priority": 2, "respond": False, "response_draft": None, "unsubscribe": False},
        {"category": "important",  "priority": 2, "respond": False, "response_draft": None, "unsubscribe": False},
        {"category": "work",       "priority": 3, "respond": False, "response_draft": None, "unsubscribe": False},
        {"category": "newsletter", "priority": 4, "respond": False, "response_draft": None, "unsubscribe": False},
        {"category": "work",       "priority": 3, "respond": False, "response_draft": None, "unsubscribe": False},
        {"category": "spam",       "priority": 5, "respond": False, "response_draft": None, "unsubscribe": False},
        {"category": "newsletter", "priority": 4, "respond": False, "response_draft": None, "unsubscribe": False},
        {"category": "spam",       "priority": 5, "respond": False, "response_draft": None, "unsubscribe": False},
    ],
}


def _post(path: str, data: dict) -> dict:
    payload = json.dumps(data).encode()
    req = urllib.request.Request(
        BASE + path, data=payload,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def _get(path: str) -> dict:
    with urllib.request.urlopen(BASE + path, timeout=10) as r:
        return json.loads(r.read())


def run_task(task_name: str, answers: list) -> float:
    rs = _post("/reset", {"task": task_name})
    print(f"\n  Task: {task_name} | emails: {rs['observation']['total_emails']}")
    rewards = []
    for i, action in enumerate(answers):
        st = _post("/step", action)
        rewards.append(st["reward"])
        email_id = "done" if not st.get("info", {}).get("email_id") else st["info"]["email_id"]
        print(f"    step {i+1}: reward={st['reward']:.2f}  {email_id}")
    mean = sum(rewards) / len(rewards) if rewards else 0.0
    print(f"  SCORE: {mean:.3f}")
    return mean


def main():
    print("Starting EmailTriage server on port 7863...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server.main:app",
         "--host", "127.0.0.1", "--port", "7863"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(5)

    try:
        h = _get("/health")
        print(f"Health: {h}")

        scores = {}
        scores["categorize-single"] = run_task(
            "categorize-single", TASK_ANSWERS["categorize-single"]
        )
        scores["inbox-triage"] = run_task(
            "inbox-triage", TASK_ANSWERS["inbox-triage"]
        )

        print("\n" + "=" * 50)
        print("SUMMARY")
        for task, score in scores.items():
            status = "PASS" if score >= 0.5 else "FAIL"
            print(f"  [{status}] {task}: {score:.3f}")
        print("=" * 50)

    finally:
        proc.terminate()
        print("Server stopped.")


if __name__ == "__main__":
    main()
