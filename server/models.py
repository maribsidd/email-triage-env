"""
Typed Pydantic models for the EmailTriage OpenEnv environment.
Defines Observation, Action, Reward, and API response models.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any

VALID_CATEGORIES = ["spam", "work", "personal", "newsletter", "important", "social"]
VALID_PRIORITIES = [1, 2, 3, 4, 5]


class Email(BaseModel):
    """A single email in the inbox."""
    id: str
    sender: str
    sender_email: str
    subject: str
    body: str
    timestamp: str
    has_attachment: bool = False


class Observation(BaseModel):
    """
    What the agent sees at each step.
    Includes the current email to process plus episode context.
    """
    current_email: Optional[Email] = None
    emails_remaining: int = Field(ge=0)
    emails_processed: int = Field(ge=0)
    total_emails: int = Field(ge=0)
    episode_reward: float = 0.0
    step: int = 0
    task_name: str = ""
    context: Dict[str, Any] = {}


class Action(BaseModel):
    """
    Agent's decision on the current email.
    - category: folder to file the email into
    - priority: urgency level 1 (critical) to 5 (ignore)
    - respond: whether to send a reply
    - response_draft: the reply content (required if respond=True for hard task scoring)
    - unsubscribe: whether to unsubscribe from this sender
    """
    category: str = Field(description="One of: spam, work, personal, newsletter, important, social")
    priority: int = Field(ge=1, le=5, description="1=critical, 2=high, 3=medium, 4=low, 5=ignore")
    respond: bool = False
    response_draft: Optional[str] = None
    unsubscribe: bool = False

    @field_validator("category")
    @classmethod
    def category_must_be_valid(cls, v: str) -> str:
        if v not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of {VALID_CATEGORIES}")
        return v


class Reward(BaseModel):
    """Detailed reward breakdown for interpretability."""
    value: float = Field(ge=0.0, le=1.0)
    breakdown: Dict[str, float] = {}
    message: str = ""


class StepResult(BaseModel):
    """Full result of a step() call."""
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any] = {}


class ResetRequest(BaseModel):
    task: str = "categorize-single"


class StateResult(BaseModel):
    """Current episode state (for debugging / human review)."""
    task_name: str
    step: int
    total_steps: int
    episode_reward: float
    emails_processed: List[Dict] = []
    current_email_id: Optional[str] = None
    done: bool = False
