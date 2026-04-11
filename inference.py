"""
EmailTriage OpenEnv — Baseline Inference Script
================================================
Runs an LLM agent against all three tasks and emits structured logs.

MANDATORY ENV VARS:
  API_BASE_URL   LLM endpoint  (default: https://router.huggingface.co/v1)
  MODEL_NAME     Model ID      (default: Qwen/Qwen2.5-72B-Instruct)
  HF_TOKEN       API key
  ENV_URL        Environment server URL (default: http://localhost:7860)
  IMAGE_NAME     Docker image name (optional — uses ENV_URL if not set)

STDOUT FORMAT:
  [START] task=<task> env=email-triage model=<model>
  [STEP]  step=<n> action=<str> reward=<0.00> done=<bool> error=<str|null>
  [END]   success=<bool> steps=<n> score=<0.000> rewards=<r1,r2,...>
"""

import asyncio
import json
import os
import textwrap
from typing import List, Optional

from openai import OpenAI

from email_triage_env import EmailTriageEnv, EmailTriageAction

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

API_KEY      = os.getenv("HF_TOKEN") or os.getenv("API_KEY") or "hf-placeholder"
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
ENV_URL      = os.getenv("ENV_URL", "http://localhost:7860")
IMAGE_NAME   = os.getenv("IMAGE_NAME", "")
BENCHMARK    = "email-triage"

TASKS = ["categorize-single", "inbox-triage", "full-inbox-manager"]
MAX_STEPS = {
    "categorize-single":   5,
    "inbox-triage":       10,
    "full-inbox-manager": 15,
}
SUCCESS_THRESHOLD = 0.5  # mean reward ≥ 0.5 → success
TEMPERATURE  = 0.2
MAX_TOKENS   = 400

# ─────────────────────────────────────────────────────────────────────────────
# Structured stdout loggers (mandatory format)
# ─────────────────────────────────────────────────────────────────────────────

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val  = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# System + user prompts
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = textwrap.dedent("""
You are an expert email triage assistant. Your job is to classify and manage emails.

For EACH email, respond ONLY with a JSON object (no markdown, no extra text):
{
  "category": "<spam|work|personal|newsletter|important|social>",
  "priority": <1-5>,
  "respond": <true|false>,
  "response_draft": "<reply text or null>",
  "unsubscribe": <true|false>
}

CATEGORY GUIDE:
  spam        — unsolicited junk, scams, phishing, casino offers
  work        — professional emails from colleagues, clients, automated work systems
  personal    — friends and family
  newsletter  — subscribed digests, marketing you may want to keep
  important   — medical, legal, financial, government, job opportunities
  social      — social media notifications

PRIORITY GUIDE:
  1 = Critical   — needs immediate action (production down, legal deadline)
  2 = High       — respond within 24h (client complaints, interview invites, family events)
  3 = Medium     — respond within a week (project updates, HR reminders)
  4 = Low        — read when convenient (newsletters, digests)
  5 = Ignore     — spam/junk, no action needed

RESPOND & RESPONSE_DRAFT:
  Set respond=true only if the email needs a reply.
  If respond=true, write a professional, relevant response_draft (50-300 chars).
  If respond=false, set response_draft to null.

UNSUBSCRIBE:
  Set unsubscribe=true only for promotional/newsletter senders you want to stop.
  Never unsubscribe from transactional or work emails.
""").strip()


def build_user_prompt(email_data: dict, step: int, total: int, task_desc: str) -> str:
    attach = " [HAS ATTACHMENT]" if email_data.get("has_attachment") else ""
    return textwrap.dedent(f"""
    Task: {task_desc}
    Email {step}/{total}{attach}

    From:    {email_data['sender']} <{email_data['sender_email']}>
    Subject: {email_data['subject']}
    Date:    {email_data['timestamp']}

    --- BODY ---
    {email_data['body']}
    --- END ---

    Respond with ONLY a JSON object. No markdown, no explanation.
    """).strip()


# ─────────────────────────────────────────────────────────────────────────────
# LLM call
# ─────────────────────────────────────────────────────────────────────────────

FALLBACK_ACTION = EmailTriageAction(
    category="work",
    priority=3,
    respond=False,
    response_draft=None,
    unsubscribe=False,
)

VALID_CATEGORIES = {"spam", "work", "personal", "newsletter", "important", "social"}


def get_model_action(
    client: OpenAI,
    email_data: dict,
    step: int,
    total: int,
    task_desc: str,
) -> tuple[EmailTriageAction, Optional[str]]:
    """Call the LLM and parse the JSON response into an EmailTriageAction."""
    prompt = build_user_prompt(email_data, step, total, task_desc)
    error: Optional[str] = None

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        raw = (completion.choices[0].message.content or "").strip()

        # Strip potential markdown fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        parsed = json.loads(raw)

        # Sanitise / clamp parsed values
        category = str(parsed.get("category", "work")).lower()
        if category not in VALID_CATEGORIES:
            category = "work"
        priority = int(parsed.get("priority", 3))
        priority = max(1, min(5, priority))
        respond  = bool(parsed.get("respond", False))
        draft    = parsed.get("response_draft") or None
        if draft and len(str(draft).strip()) < 5:
            draft = None
        unsub = bool(parsed.get("unsubscribe", False))

        return EmailTriageAction(
            category=category,
            priority=priority,
            respond=respond,
            response_draft=str(draft) if draft else None,
            unsubscribe=unsub,
        ), None

    except json.JSONDecodeError as e:
        error = f"json_parse_error: {e}"
    except Exception as e:
        error = f"llm_error: {type(e).__name__}: {e}"

    return FALLBACK_ACTION, error


# ─────────────────────────────────────────────────────────────────────────────
# Episode runner
# ─────────────────────────────────────────────────────────────────────────────

async def run_episode(
    env: EmailTriageEnv,
    client: OpenAI,
    task_name: str,
) -> dict:
    """Run one full episode and return summary stats."""
    rewards:     List[float] = []
    steps_taken: int         = 0
    success      = False
    score        = 0.0

    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    try:
        result = await env.reset(task=task_name)
        obs    = result.observation
        task_desc = obs.context.get("task_description", task_name)

        for step_n in range(1, MAX_STEPS[task_name] + 1):
            if result.done or obs.current_email is None:
                break

            email_dict = {
                "id":             obs.current_email.id,
                "sender":         obs.current_email.sender,
                "sender_email":   obs.current_email.sender_email,
                "subject":        obs.current_email.subject,
                "body":           obs.current_email.body,
                "timestamp":      obs.current_email.timestamp,
                "has_attachment": obs.current_email.has_attachment,
            }

            action, error = get_model_action(
                client, email_dict, step_n, obs.total_emails, task_desc
            )
            action_str = (
                f"category={action.category},priority={action.priority},"
                f"respond={action.respond},unsubscribe={action.unsubscribe}"
            )

            result = await env.step(action)
            obs    = result.observation

            rewards.append(result.reward)
            steps_taken = step_n

            log_step(
                step=step_n,
                action=action_str,
                reward=result.reward,
                done=result.done,
                error=error,
            )

            if result.done:
                break

        score   = sum(rewards) / len(rewards) if rewards else 0.0
        score   = round(min(max(score, 0.0), 1.0), 4)
        success = score >= SUCCESS_THRESHOLD

    except Exception as exc:
        print(f"[DEBUG] Episode error: {exc}", flush=True)

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return {
        "task":    task_name,
        "score":   score,
        "success": success,
        "steps":   steps_taken,
        "rewards": rewards,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

async def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    # Connect to environment — prefer Docker image, fall back to running server
    if IMAGE_NAME:
        env = await EmailTriageEnv.from_docker_image(IMAGE_NAME)
    else:
        env = EmailTriageEnv(base_url=ENV_URL, task="categorize-single")

    results = []
    try:
        for task_name in TASKS:
            summary = await run_episode(env, client, task_name)
            results.append(summary)
    finally:
        await env.close()

    # Print overall summary
    print("\n[SUMMARY]", flush=True)
    for r in results:
        status = "✓ PASS" if r["success"] else "✗ FAIL"
        print(
            f"  {status}  task={r['task']:25s}  score={r['score']:.3f}  steps={r['steps']}",
            flush=True,
        )
    overall = sum(r["score"] for r in results) / len(results) if results else 0.0
    print(f"  OVERALL  mean_score={overall:.3f}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
