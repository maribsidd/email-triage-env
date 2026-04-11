"""
Core EmailTriageEnvironment — manages episode state, processes actions,
computes rewards, and tracks history.
"""

from typing import Optional, List, Dict, Any

from .models import Observation, Action, Email, StepResult, StateResult
from .tasks import get_task, get_task_emails, TASK_CONFIGS
from .graders import grade_step


class EmailTriageEnv:
    """
    Stateful environment for one episode of email triage.

    Episode lifecycle:
      reset(task) → step(action) × N → done=True

    Each step presents one email; the agent must classify,
    prioritize, optionally draft a reply, and decide whether to unsubscribe.
    """

    def __init__(self) -> None:
        self._task_name: str = ""
        self._emails: List[Dict[str, Any]] = []
        self._scoring_weights: Dict[str, float] = {}
        self._step_idx: int = 0
        self._episode_reward: float = 0.0
        self._history: List[Dict[str, Any]] = []
        self._done: bool = False

    # ──────────────────────────────────────────────────────────────
    # OpenEnv API
    # ──────────────────────────────────────────────────────────────

    def reset(self, task_name: str = "categorize-single") -> StepResult:
        """Start a new episode for the given task."""
        config = get_task(task_name)           # raises ValueError for unknown tasks
        self._task_name       = task_name
        self._emails          = get_task_emails(task_name)
        self._scoring_weights = config["scoring"]
        self._step_idx        = 0
        self._episode_reward  = 0.0
        self._history         = []
        self._done            = False

        obs = self._make_observation()
        return StepResult(observation=obs, reward=0.0, done=False, info={"task": task_name})

    def step(self, action: Action) -> StepResult:
        """Process the agent's action on the current email."""
        if self._done:
            raise RuntimeError("Episode is finished — call reset() to start a new one.")
        if self._step_idx >= len(self._emails):
            self._done = True
            return StepResult(
                observation=self._make_observation(),
                reward=0.0,
                done=True,
                info={"message": "No more emails — episode complete."},
            )

        current_email = self._emails[self._step_idx]

        # Grade the action
        result = grade_step(
            action=action.model_dump(),
            email=current_email,
            scoring_weights=self._scoring_weights,
        )

        reward = result["reward"]
        self._episode_reward += reward
        self._history.append({
            "step":      self._step_idx + 1,
            "email_id":  current_email["id"],
            "action":    action.model_dump(),
            "reward":    reward,
            "breakdown": result["breakdown"],
            "message":   result["message"],
        })

        self._step_idx += 1
        done = self._step_idx >= len(self._emails)
        self._done = done

        obs = self._make_observation()

        info = {
            "email_id":   current_email["id"],
            "grading":    result["breakdown"],
            "message":    result["message"],
        }
        if done:
            n = len(self._emails)
            mean_reward = self._episode_reward / n if n > 0 else 0.0
            info["episode_summary"] = {
                "total_reward":  round(self._episode_reward, 4),
                "mean_reward":   round(mean_reward, 4),
                "steps":         self._step_idx,
                "final_score":   round(mean_reward, 4),
            }

        return StepResult(observation=obs, reward=reward, done=done, info=info)

    def state(self) -> StateResult:
        """Return current episode state (for debugging / evaluation)."""
        current_id: Optional[str] = None
        if 0 <= self._step_idx < len(self._emails):
            current_id = self._emails[self._step_idx]["id"]

        return StateResult(
            task_name=self._task_name,
            step=self._step_idx,
            total_steps=len(self._emails),
            episode_reward=round(self._episode_reward, 4),
            emails_processed=[
                {
                    "email_id": h["email_id"],
                    "step":     h["step"],
                    "reward":   h["reward"],
                    "message":  h["message"],
                }
                for h in self._history
            ],
            current_email_id=current_id,
            done=self._done,
        )

    # ──────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────

    def _make_observation(self) -> Observation:
        emails_remaining = max(0, len(self._emails) - self._step_idx)
        current_email_obj: Optional[Email] = None

        if 0 <= self._step_idx < len(self._emails):
            e = self._emails[self._step_idx]
            current_email_obj = Email(
                id=e["id"],
                sender=e["sender"],
                sender_email=e["sender_email"],
                subject=e["subject"],
                body=e["body"],
                timestamp=e["timestamp"],
                has_attachment=e.get("has_attachment", False),
            )

        context: Dict[str, Any] = {}
        if self._task_name in TASK_CONFIGS:
            cfg = TASK_CONFIGS[self._task_name]
            context["task_description"] = cfg["description"]
            context["difficulty"]       = cfg["difficulty"]
            context["scoring_weights"]  = self._scoring_weights

        return Observation(
            current_email=current_email_obj,
            emails_remaining=emails_remaining,
            emails_processed=self._step_idx,
            total_emails=len(self._emails),
            episode_reward=round(self._episode_reward, 4),
            step=self._step_idx,
            task_name=self._task_name,
            context=context,
        )


# Global singleton — one session at a time (sufficient for hackathon scope)
_env_instance = EmailTriageEnv()


def get_env() -> EmailTriageEnv:
    return _env_instance
