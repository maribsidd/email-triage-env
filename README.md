---
title: EmailTriage OpenEnv
emoji: 📧
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
license: mit
tags:
  - openenv
---

# 📧 EmailTriage OpenEnv

A complete **OpenEnv-compliant** reinforcement learning environment that trains and evaluates AI agents on real-world **email triage** — one of the most universal productivity tasks in knowledge work.

---

## Why Email Triage?

Every knowledge worker spends ~28% of their work week managing email (McKinsey, 2012 — and it has only grown). A competent agent must:

- **Classify** email intent and content (work vs. spam vs. personal vs. legal)
- **Prioritize** urgency without over-alerting or missing critical items  
- **Draft professional responses** that are relevant, appropriately toned, and concise
- **Manage subscriptions** — unsubscribe from unwanted senders without nuking legitimate channels

This environment models all four of these skills with a rich reward signal, partial credit grading, and three calibrated difficulty levels.

---

## Quickstart

### Option A — Docker (recommended)

```bash
docker build -t email-triage-env .
docker run -p 7860:7860 email-triage-env
```

Then in another terminal:

```bash
pip install -r requirements-client.txt
export HF_TOKEN=your_hf_token
python inference.py
```

### Option B — Local (no Docker)

```bash
pip install -r requirements.txt
uvicorn server.main:app --port 7860
```

---

## API Reference

All endpoints return JSON. The server runs on port **7860**.

### `POST /reset`

Start a new episode.

```json
{ "task": "categorize-single" }
```

Returns a `StepResult` with the first email in `observation.current_email`.

### `POST /step`

Submit an action for the current email.

```json
{
  "category": "work",
  "priority": 2,
  "respond": true,
  "response_draft": "Dear Sarah, I'm on track for the deadline. Will send an update by EOD.",
  "unsubscribe": false
}
```

Returns a `StepResult` with the next email, the step reward, and a grading breakdown in `info`.

### `GET /state`

Inspect the current episode state (useful for debugging).

### `GET /tasks`

List all available tasks.

---

## Observation Space

| Field | Type | Description |
|---|---|---|
| `current_email.id` | string | Unique email ID |
| `current_email.sender` | string | Display name |
| `current_email.sender_email` | string | Email address |
| `current_email.subject` | string | Email subject |
| `current_email.body` | string | Full email body |
| `current_email.timestamp` | string (ISO 8601) | Received time |
| `current_email.has_attachment` | boolean | Whether file attached |
| `emails_remaining` | int | Emails left in episode |
| `emails_processed` | int | Emails processed so far |
| `total_emails` | int | Total emails in task |
| `episode_reward` | float | Cumulative reward |
| `step` | int | Current step index |
| `task_name` | string | Active task |
| `context` | object | Task description, difficulty, scoring weights |

## Action Space

| Field | Type | Values |
|---|---|---|
| `category` | string | `spam`, `work`, `personal`, `newsletter`, `important`, `social` |
| `priority` | int | 1 (critical) → 5 (ignore) |
| `respond` | bool | Whether to draft a reply |
| `response_draft` | string / null | Reply content |
| `unsubscribe` | bool | Whether to unsubscribe from sender |

---

## Tasks

### 🟢 Easy — `categorize-single`

**5 emails**, scored on **category accuracy only**.

The agent processes one email at a time and must place it in the correct folder. Emails span all categories (spam, work, personal, newsletter, important) with clear, unambiguous content. Good for verifying basic email understanding.

**Expected baseline score (GPT-4 class):** ~0.85

---

### 🟡 Medium — `inbox-triage`

**10 emails**, scored on **50% category + 50% priority accuracy**.

Mixed inbox including a production incident (priority 1), client complaint (priority 2), HR reminder (priority 3), newsletters (priority 4), and spam (priority 5). The agent must both classify AND correctly gauge urgency with partial credit for near-misses.

**Expected baseline score (GPT-4 class):** ~0.70

---

### 🔴 Hard — `full-inbox-manager`

**15 emails**, scored on **30% category + 30% priority + 30% response quality + 10% unsubscribe**.

Full inbox management. Five emails require drafted responses (production incident, client complaint, legal notice, family RSVP, support ticket). One promotional newsletter should be unsubscribed. Response quality scored on: greeting, topic relevance, professional closing, appropriate length, and tone.

**Expected baseline score (GPT-4 class):** ~0.55

---

## Reward Function

Each step returns a reward in **[0.0, 1.0]**:

### Category Score
- Exact match: **1.0**
- Adjacent category (e.g. spam↔newsletter, work↔important): **0.3**
- Total miss: **0.0**

### Priority Score
- Exact: **1.0** | Off by 1: **0.6** | Off by 2: **0.2** | Off by 3+: **0.0**

### Response Quality Score (hard task)
| Criterion | Weight |
|---|---|
| Greeting (Dear/Hi/Hello) | 0.15 |
| Topic relevance (keyword overlap) | 0.40 |
| Professional closing | 0.15 |
| Appropriate length (80–500 chars) | 0.20 |
| Professionalism (capitalization, punctuation) | 0.10 |

### Unsubscribe Score
- Correct decision: **1.0** | Wrong: **0.2** (partial credit)

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `API_BASE_URL` | `https://router.huggingface.co/v1` | LLM endpoint |
| `MODEL_NAME` | `Qwen/Qwen2.5-72B-Instruct` | Model identifier |
| `HF_TOKEN` | — | HuggingFace / API key |
| `ENV_URL` | `http://localhost:7860` | Environment server URL |
| `IMAGE_NAME` | — | Docker image (if using from_docker_image) |

---

## Project Structure

```
email-triage-env/
├── Dockerfile                  # Container definition (port 7860)
├── openenv.yaml                # OpenEnv spec metadata
├── requirements.txt            # Server dependencies
├── requirements-client.txt     # Inference/client dependencies
├── inference.py                # Baseline inference script
├── email_triage_env.py         # Python client class
└── server/
    ├── main.py                 # FastAPI app + endpoints
    ├── env.py                  # Core environment state machine
    ├── models.py               # Pydantic typed models
    ├── tasks.py                # Email corpus + task configs
    └── graders.py              # Deterministic grading functions
```

---

## Baseline Scores

Run `python inference.py` with a live server to reproduce.

| Task | Difficulty | Qwen2.5-72B Score |
|---|---|---|
| `categorize-single` | Easy | ~0.85 |
| `inbox-triage` | Medium | ~0.70 |
| `full-inbox-manager` | Hard | ~0.55 |

---

## HuggingFace Spaces

Deployed at: `https://huggingface.co/spaces/<your-username>/email-triage-env`

The Space runs the FastAPI server directly from the Dockerfile, exposing the full OpenEnv API at the Space URL.
