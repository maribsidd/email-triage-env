"""
Deterministic graders for the EmailTriage environment.

Each grader scores an agent action against the ground truth annotation
and returns a reward in [0.0, 1.0] with a detailed breakdown.
"""

from typing import Dict, Any, Optional


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORY GRADING
# ─────────────────────────────────────────────────────────────────────────────

# Adjacency map — partial credit for semantically close categories
_ADJACENT: Dict[str, list] = {
    "spam":       ["newsletter"],
    "newsletter": ["spam"],
    "work":       ["important"],
    "important":  ["work"],
    "personal":   ["social"],
    "social":     ["personal"],
}


def score_category(predicted: str, ground_truth: str) -> float:
    """
    1.0 — exact match
    0.3 — adjacent/related category
    0.0 — total miss
    """
    if predicted == ground_truth:
        return 1.0
    if predicted in _ADJACENT.get(ground_truth, []):
        return 0.3
    return 0.0


# ─────────────────────────────────────────────────────────────────────────────
# PRIORITY GRADING
# ─────────────────────────────────────────────────────────────────────────────

def score_priority(predicted: int, ground_truth: int) -> float:
    """
    1.0 — exact match
    0.6 — off by 1
    0.2 — off by 2
    0.0 — off by 3+
    """
    delta = abs(predicted - ground_truth)
    if delta == 0:
        return 1.0
    if delta == 1:
        return 0.6
    if delta == 2:
        return 0.2
    return 0.0


# ─────────────────────────────────────────────────────────────────────────────
# RESPONSE QUALITY GRADING
# ─────────────────────────────────────────────────────────────────────────────

_GREETINGS = ["dear", "hi ", "hello", "good morning", "good afternoon", "good evening", "hey"]
_CLOSINGS  = ["best", "regards", "thanks", "thank you", "sincerely", "cheers",
              "looking forward", "warm regards", "yours", "respectfully"]


def _extract_keywords(email: Dict[str, Any]) -> list:
    """Pull meaningful keywords from subject + first lines of body."""
    subject_words = [w.lower().strip(".,!?:") for w in email["subject"].split() if len(w) > 3]
    body_words    = [w.lower().strip(".,!?:") for w in email["body"].split()[:80] if len(w) > 4]
    stopwords = {"your", "with", "that", "this", "from", "have", "will", "been",
                 "they", "their", "about", "more", "over", "also", "some", "into"}
    keywords = [w for w in set(subject_words + body_words) if w not in stopwords]
    return keywords[:12]  # cap at 12 to avoid noise


def score_response_quality(
    response_draft: Optional[str],
    email: Dict[str, Any],
    email_requires_response: bool,
) -> float:
    """
    Scores the quality of a drafted response (0.0–1.0).

    If the email does NOT require a response:
      - Drafting one = 0.1 penalty (unnecessary noise, but not catastrophic)
      - Not drafting = 1.0

    If the email DOES require a response:
      - No draft = 0.0
      - Draft scored on: greeting, relevance, closing, length, professionalism
    """
    if not email_requires_response:
        # Bonus for not writing unnecessary replies
        return 0.9 if (not response_draft or len(response_draft.strip()) < 10) else 0.6

    if not response_draft or len(response_draft.strip()) < 15:
        return 0.0

    text = response_draft.strip()
    text_lower = text.lower()
    score = 0.0

    # 1. Greeting (0.15)
    if any(text_lower.startswith(g) for g in _GREETINGS):
        score += 0.15

    # 2. Topic relevance (0.40) — checks if keywords from the email appear in draft
    keywords = _extract_keywords(email)
    matched = sum(1 for kw in keywords if kw in text_lower)
    relevance = min(1.0, matched / max(len(keywords), 3))
    score += 0.40 * relevance

    # 3. Closing statement (0.15)
    tail = text_lower[-120:]
    if any(c in tail for c in _CLOSINGS):
        score += 0.15

    # 4. Appropriate length (0.20)
    ln = len(text)
    if 80 <= ln <= 500:
        score += 0.20
    elif 40 <= ln < 80 or 500 < ln <= 800:
        score += 0.10

    # 5. Professionalism (0.10)
    exclamations = text.count("!")
    starts_with_capital = text[0].isupper() if text else False
    if exclamations <= 2 and starts_with_capital:
        score += 0.10
    elif starts_with_capital:
        score += 0.05

    return round(min(score, 1.0), 4)


# ─────────────────────────────────────────────────────────────────────────────
# UNSUBSCRIBE GRADING
# ─────────────────────────────────────────────────────────────────────────────

def score_unsubscribe(predicted: bool, ground_truth: bool) -> float:
    """
    1.0 — correct decision
    0.2 — wrong but email is a newsletter (minor mistake)
    0.0 — tried to unsubscribe from non-newsletter / spam
    """
    if predicted == ground_truth:
        return 1.0
    return 0.2  # minor partial credit for close-but-wrong


# ─────────────────────────────────────────────────────────────────────────────
# COMPOSITE STEP GRADER
# ─────────────────────────────────────────────────────────────────────────────

def grade_step(
    action: Dict[str, Any],
    email: Dict[str, Any],
    scoring_weights: Dict[str, float],
) -> Dict[str, Any]:
    """
    Grade a single step action against the email's ground truth.

    Returns:
        {
          "reward": float,          # composite weighted score in [0.0, 1.0]
          "breakdown": {            # per-component scores
            "category": float,
            "priority": float,
            "response": float,
            "unsubscribe": float
          },
          "ground_truth": dict,     # for logging
          "message": str            # human-readable explanation
        }
    """
    gt = email["ground_truth"]

    cat_score   = score_category(action["category"], gt["category"])
    pri_score   = score_priority(action["priority"], gt["priority"])
    resp_score  = score_response_quality(
        action.get("response_draft"),
        email,
        gt["requires_response"],
    )
    unsub_score = score_unsubscribe(action.get("unsubscribe", False), gt["requires_unsubscribe"])

    w = scoring_weights
    reward = (
        w.get("category_weight", 0.0)    * cat_score
        + w.get("priority_weight", 0.0)  * pri_score
        + w.get("response_weight", 0.0)  * resp_score
        + w.get("unsubscribe_weight", 0.0) * unsub_score
    )
    reward = round(min(max(reward, 0.0), 1.0), 4)

    messages = []
    if cat_score == 1.0:
        messages.append(f"Category '{action['category']}' ✓")
    else:
        messages.append(f"Category: got '{action['category']}', expected '{gt['category']}' (score={cat_score:.1f})")

    if w.get("priority_weight", 0) > 0:
        if pri_score == 1.0:
            messages.append(f"Priority {action['priority']} ✓")
        else:
            messages.append(f"Priority: got {action['priority']}, expected {gt['priority']} (score={pri_score:.1f})")

    return {
        "reward": reward,
        "breakdown": {
            "category":    round(cat_score, 4),
            "priority":    round(pri_score, 4),
            "response":    round(resp_score, 4),
            "unsubscribe": round(unsub_score, 4),
        },
        "ground_truth": gt,
        "message": " | ".join(messages),
    }
