"""
Email dataset and task definitions for the EmailTriage environment.

15 realistic emails covering spam, work, personal, newsletters, and important messages.
Three task configs with easy → medium → hard difficulty.
"""

from typing import List, Dict, Any

# ─────────────────────────────────────────────────────────────────────────────
# EMAIL CORPUS (15 emails, fully annotated)
# ─────────────────────────────────────────────────────────────────────────────

EMAILS: Dict[str, Dict[str, Any]] = {

    "spam_001": {
        "id": "spam_001",
        "sender": "International Prize Committee",
        "sender_email": "winner@global-prize-alert.biz",
        "subject": "URGENT: You Have Won $1,000,000 - Claim Within 24 Hours!",
        "body": (
            "Dear Lucky Winner,\n\n"
            "Congratulations! Your email address was randomly selected in our International "
            "Email Sweepstakes. You have been awarded the sum of ONE MILLION DOLLARS "
            "($1,000,000 USD) in our quarterly draw.\n\n"
            "To process your winnings, kindly reply with: Full Name, Address, "
            "Phone Number, and Bank Account Details.\n\n"
            "This offer expires in 24 HOURS. Do not miss this once-in-a-lifetime opportunity!\n\n"
            "Best Regards,\nDr. James Wellington\nPrize Disbursement Officer"
        ),
        "timestamp": "2024-01-15T08:23:00Z",
        "has_attachment": False,
        "ground_truth": {
            "category": "spam",
            "priority": 5,
            "requires_response": False,
            "requires_unsubscribe": False,
        },
    },

    "work_001": {
        "id": "work_001",
        "sender": "Sarah Johnson",
        "sender_email": "sarah.johnson@acmecorp.com",
        "subject": "Project Alpha - Updated Deadline & Deliverables",
        "body": (
            "Hi,\n\n"
            "Following yesterday's sprint review, the Project Alpha deadline has been moved "
            "to January 26th. The client has confirmed the final feature list:\n\n"
            "- Dashboard redesign (yours)\n"
            "- API integration layer\n"
            "- QA sign-off by Jan 24th\n\n"
            "Can you confirm you're on track? Let me know if you need additional resources.\n\n"
            "Thanks,\nSarah\nProject Manager, ACME Corp"
        ),
        "timestamp": "2024-01-15T09:10:00Z",
        "has_attachment": False,
        "ground_truth": {
            "category": "work",
            "priority": 3,
            "requires_response": False,
            "requires_unsubscribe": False,
        },
    },

    "personal_001": {
        "id": "personal_001",
        "sender": "James Chen",
        "sender_email": "james.chen.personal@gmail.com",
        "subject": "BBQ at my place this Saturday! 🍖",
        "body": (
            "Hey!\n\n"
            "Hosting a BBQ this Saturday (Jan 20) from 4 PM at my place. "
            "Bringing the grill out, should be a great time. "
            "Let me know if you can make it — just bring drinks!\n\n"
            "Address: 42 Maple Street (same as last time)\n\n"
            "Cheers,\nJames"
        ),
        "timestamp": "2024-01-15T10:05:00Z",
        "has_attachment": False,
        "ground_truth": {
            "category": "personal",
            "priority": 3,
            "requires_response": False,
            "requires_unsubscribe": False,
        },
    },

    "newsletter_001": {
        "id": "newsletter_001",
        "sender": "TechCrunch",
        "sender_email": "digest@techcrunch.com",
        "subject": "TechCrunch Weekly Digest — Top Stories This Week",
        "body": (
            "TechCrunch Weekly Digest | January 15, 2024\n\n"
            "TOP STORIES:\n"
            "• OpenAI announces new enterprise features for ChatGPT\n"
            "• Startup funding rounds hit $12B in Q4 2023\n"
            "• Google DeepMind unveils AlphaCode 2 benchmarks\n"
            "• Apple Vision Pro pre-orders open January 19\n\n"
            "Read more at techcrunch.com\n\n"
            "To unsubscribe from this newsletter, click here."
        ),
        "timestamp": "2024-01-15T07:00:00Z",
        "has_attachment": False,
        "ground_truth": {
            "category": "newsletter",
            "priority": 4,
            "requires_response": False,
            "requires_unsubscribe": False,
        },
    },

    "important_001": {
        "id": "important_001",
        "sender": "Apollo Diagnostics",
        "sender_email": "noreply@apollo-diagnostics.com",
        "subject": "Your Lab Test Results Are Now Available",
        "body": (
            "Dear Patient,\n\n"
            "Your laboratory test results from January 14, 2024 are now available "
            "in your patient portal.\n\n"
            "Reference ID: APL-2024-78342\n"
            "Tests Completed: Complete Blood Count, Lipid Panel, HbA1c\n\n"
            "Please log in to your portal to review your results. "
            "Your doctor may follow up if any values require attention.\n\n"
            "Portal: https://portal.apollo-diagnostics.com\n\n"
            "Apollo Diagnostics Patient Services"
        ),
        "timestamp": "2024-01-15T11:30:00Z",
        "has_attachment": False,
        "ground_truth": {
            "category": "important",
            "priority": 2,
            "requires_response": False,
            "requires_unsubscribe": False,
        },
    },

    "work_002": {
        "id": "work_002",
        "sender": "PagerDuty Alerts",
        "sender_email": "alerts@monitor.acmecorp.com",
        "subject": "🔴 CRITICAL: Production API Server Down — All Services Affected",
        "body": (
            "INCIDENT ALERT — SEVERITY: CRITICAL\n\n"
            "Service: Production API Gateway\n"
            "Status: DOWN\n"
            "Time Detected: 2024-01-15 12:47 UTC\n"
            "Impact: 100% of API requests failing. All customer-facing services unavailable.\n"
            "Error: Connection timeout on primary cluster. Failover did not trigger.\n\n"
            "Assigned On-Call: You\n"
            "Escalation in: 15 minutes if unacknowledged\n\n"
            "ACK this alert: https://pagerduty.acmecorp.com/ack/INC-4471\n\n"
            "PagerDuty | ACME Corp Engineering"
        ),
        "timestamp": "2024-01-15T12:47:00Z",
        "has_attachment": False,
        "ground_truth": {
            "category": "work",
            "priority": 1,
            "requires_response": True,
            "requires_unsubscribe": False,
            "response_keywords": ["acknowledge", "looking", "investigating", "incident", "escalate"],
        },
    },

    "work_003": {
        "id": "work_003",
        "sender": "Mike Ross",
        "sender_email": "mike.ross@bigclient.com",
        "subject": "Extremely disappointed with your service — formal complaint",
        "body": (
            "To Whom It May Concern,\n\n"
            "I am writing to formally complain about the service I received on January 12th. "
            "Our order (#ORD-9923) arrived three days late, and two items were incorrect. "
            "We are a premium account holder paying $2,000/month and this is unacceptable.\n\n"
            "I expect a full explanation, a refund for the incorrect items, and a service credit "
            "within 48 hours — or I will be taking our business elsewhere.\n\n"
            "Mike Ross\nCTO, BigClient Inc."
        ),
        "timestamp": "2024-01-15T13:15:00Z",
        "has_attachment": False,
        "ground_truth": {
            "category": "work",
            "priority": 2,
            "requires_response": True,
            "requires_unsubscribe": False,
            "response_keywords": ["apologize", "sorry", "refund", "resolve", "credit", "investigate"],
        },
    },

    "work_004": {
        "id": "work_004",
        "sender": "HR Department",
        "sender_email": "hr@acmecorp.com",
        "subject": "Annual Performance Review Submissions — Deadline Jan 31",
        "body": (
            "Hi All,\n\n"
            "Friendly reminder that annual performance review self-assessments are due by "
            "January 31st. Please log into Workday to complete your self-review and set "
            "goals for 2024.\n\n"
            "Steps:\n"
            "1. Log in to Workday\n"
            "2. Navigate to Performance → My Review\n"
            "3. Complete all sections\n\n"
            "Questions? Contact hr@acmecorp.com\n\n"
            "HR Department\nACME Corp"
        ),
        "timestamp": "2024-01-15T09:45:00Z",
        "has_attachment": False,
        "ground_truth": {
            "category": "work",
            "priority": 3,
            "requires_response": False,
            "requires_unsubscribe": False,
        },
    },

    "newsletter_002": {
        "id": "newsletter_002",
        "sender": "Medium Daily Digest",
        "sender_email": "noreply@medium.com",
        "subject": "Your personalized reading list for today",
        "body": (
            "Good morning!\n\n"
            "Based on your reading history, we've curated these stories for you:\n\n"
            "1. 'Why Most Developers Get System Design Wrong' — 8 min read\n"
            "2. 'The Hidden Psychology Behind Procrastination' — 6 min read\n"
            "3. 'Building Micro-SaaS Products in 2024' — 12 min read\n\n"
            "Upgrade to Medium Premium for unlimited access.\n\n"
            "Manage your email preferences | Unsubscribe\n"
            "© Medium, LLC"
        ),
        "timestamp": "2024-01-15T06:30:00Z",
        "has_attachment": False,
        "ground_truth": {
            "category": "newsletter",
            "priority": 4,
            "requires_response": False,
            "requires_unsubscribe": False,
        },
    },

    "spam_002": {
        "id": "spam_002",
        "sender": "VegasCasino Rewards",
        "sender_email": "offers@vegascasino-winbig.net",
        "subject": "🎰 500 FREE Spins Waiting For You — Expires Tonight!",
        "body": (
            "YOU'VE BEEN SELECTED FOR AN EXCLUSIVE OFFER!\n\n"
            "Claim your 500 FREE SPINS on our hottest slot games!\n"
            "No deposit required. Win REAL CASH today!\n\n"
            "🎁 BONUS: $100 match on your first deposit\n"
            "⏰ This offer expires at midnight\n\n"
            "CLICK HERE TO CLAIM YOUR FREE SPINS NOW\n\n"
            "VegasCasino | Gambling can be addictive. Play responsibly.\n"
            "Unsubscribe | Terms & Conditions"
        ),
        "timestamp": "2024-01-15T10:20:00Z",
        "has_attachment": False,
        "ground_truth": {
            "category": "spam",
            "priority": 5,
            "requires_response": False,
            "requires_unsubscribe": False,
        },
    },

    "important_002": {
        "id": "important_002",
        "sender": "Google Recruiting",
        "sender_email": "recruiting@google.com",
        "subject": "Software Engineer Interview Invitation — Google India",
        "body": (
            "Dear Candidate,\n\n"
            "Following your application for the Software Engineer role at Google India, "
            "we are pleased to invite you to the next round of interviews.\n\n"
            "Round: Technical Phone Screen\n"
            "Available slots: Jan 22–25, 2024\n"
            "Duration: 45 minutes\n"
            "Format: LeetCode-style coding problem + system design discussion\n\n"
            "Please reply to this email within 3 business days to schedule your interview. "
            "If you have any questions, reply directly to this message.\n\n"
            "Best,\nPriya Sharma\nTechnical Recruiting, Google India"
        ),
        "timestamp": "2024-01-15T14:00:00Z",
        "has_attachment": False,
        "ground_truth": {
            "category": "important",
            "priority": 2,
            "requires_response": False,
            "requires_unsubscribe": False,
        },
    },

    "work_005": {
        "id": "work_005",
        "sender": "Support Ticket System",
        "sender_email": "tickets@support.acmecorp.com",
        "subject": "[Ticket #45821] Customer: Login page broken on Safari",
        "body": (
            "Ticket ID: #45821\n"
            "Customer: Priya Nair (priya.nair@startup.io)\n"
            "Priority: High\n"
            "Created: 2024-01-15 11:02 UTC\n\n"
            "Customer Message:\n"
            "'Hi, I cannot log into the platform on Safari (Version 17.2). "
            "The login button does nothing when I click it. "
            "Chrome works fine. This is blocking my entire team. Please help urgently.'\n\n"
            "This ticket has been assigned to you. "
            "Please respond within 4 hours per our SLA.\n\n"
            "Support System | ACME Corp"
        ),
        "timestamp": "2024-01-15T11:05:00Z",
        "has_attachment": False,
        "ground_truth": {
            "category": "work",
            "priority": 3,
            "requires_response": True,
            "requires_unsubscribe": False,
            "response_keywords": ["safari", "investigating", "fix", "workaround", "ticket", "team"],
        },
    },

    "personal_002": {
        "id": "personal_002",
        "sender": "Mom",
        "sender_email": "mom@family.com",
        "subject": "Grandma's 80th Birthday — Can you make it?",
        "body": (
            "Sweetheart,\n\n"
            "As you know, Grandma turns 80 on February 3rd. We're planning a surprise party "
            "at Uncle Raj's farm on Saturday February 1st, starting at 6 PM.\n\n"
            "Your cousin Anita is flying in from London. It would mean the world to Grandma "
            "if you could be there.\n\n"
            "Can you please let me know if you're coming? We need the final headcount "
            "by January 20th for the catering.\n\n"
            "Love,\nMom 💕"
        ),
        "timestamp": "2024-01-15T16:00:00Z",
        "has_attachment": False,
        "ground_truth": {
            "category": "personal",
            "priority": 2,
            "requires_response": True,
            "requires_unsubscribe": False,
            "response_keywords": ["grandma", "coming", "party", "birthday", "yes", "attend"],
        },
    },

    "newsletter_003": {
        "id": "newsletter_003",
        "sender": "FashionHub Deals",
        "sender_email": "promo@fashionhub-deals.com",
        "subject": "🛍️ Your EXCLUSIVE Member Deal: 70% OFF Expires in 2 Hours!",
        "body": (
            "Hey VIP Member!\n\n"
            "Just for you: 70% OFF on everything in our Winter Collection!\n"
            "Use code: VIP70 at checkout.\n\n"
            "✅ Free shipping on orders over ₹499\n"
            "✅ Easy returns\n"
            "✅ 10,000+ happy customers\n\n"
            "This deal expires in 2 HOURS. Don't miss out!\n\n"
            "SHOP NOW → fashionhub-deals.com\n\n"
            "You're receiving this because you signed up at FashionHub.\n"
            "Unsubscribe from promotional emails | Manage preferences"
        ),
        "timestamp": "2024-01-15T15:30:00Z",
        "has_attachment": False,
        "ground_truth": {
            "category": "newsletter",
            "priority": 5,
            "requires_response": False,
            "requires_unsubscribe": True,
        },
    },

    "important_003": {
        "id": "important_003",
        "sender": "Mehta & Associates — Legal",
        "sender_email": "advocate@mehta-legal.com",
        "subject": "Legal Notice: Response Required Within 7 Days — Re: Property Dispute",
        "body": (
            "Dear Sir/Madam,\n\n"
            "This firm represents Mr. Rajesh Gupta in the matter of the property dispute "
            "at 14-B Rajpur Road. Our client asserts ownership of the disputed 200 sq. ft. "
            "portion based on registered deed No. DL-2009-4432.\n\n"
            "You are hereby notified to respond to this legal notice within 7 (seven) days "
            "of receipt, failing which our client reserves the right to pursue legal remedies "
            "including filing a civil suit in the appropriate court.\n\n"
            "Please contact us at the number below or respond in writing.\n\n"
            "Adv. Sunita Mehta | Mehta & Associates\n"
            "Tel: 011-4455-6677"
        ),
        "timestamp": "2024-01-15T14:45:00Z",
        "has_attachment": True,
        "ground_truth": {
            "category": "important",
            "priority": 1,
            "requires_response": True,
            "requires_unsubscribe": False,
            "response_keywords": ["legal", "notice", "received", "consult", "lawyer", "respond", "advocate"],
        },
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# TASK DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

TASK_CONFIGS: Dict[str, Dict[str, Any]] = {

    "categorize-single": {
        "name": "categorize-single",
        "display_name": "Email Categorization",
        "difficulty": "easy",
        "description": (
            "Categorize each email into the correct folder. "
            "Focus on category accuracy — priority and response are not scored."
        ),
        "email_ids": [
            "spam_001",       # obvious spam
            "work_001",       # work project update
            "personal_001",   # friend BBQ invite
            "newsletter_001", # TechCrunch digest
            "important_001",  # medical lab results
        ],
        "scoring": {
            "category_weight": 1.0,
            "priority_weight": 0.0,
            "response_weight": 0.0,
            "unsubscribe_weight": 0.0,
        },
        "max_steps": 5,
    },

    "inbox-triage": {
        "name": "inbox-triage",
        "display_name": "Inbox Triage",
        "difficulty": "medium",
        "description": (
            "Triage a mixed 10-email inbox. "
            "Correctly categorize each email AND assign the right urgency priority. "
            "Partial credit for priorities within 1 level."
        ),
        "email_ids": [
            "work_002",       # CRITICAL server down
            "work_003",       # client complaint
            "important_001",  # lab results
            "important_002",  # Google interview
            "work_001",       # project deadline
            "newsletter_001", # TechCrunch
            "work_004",       # HR review
            "spam_001",       # lottery scam
            "newsletter_002", # Medium digest
            "spam_002",       # casino spam
        ],
        "scoring": {
            "category_weight": 0.5,
            "priority_weight": 0.5,
            "response_weight": 0.0,
            "unsubscribe_weight": 0.0,
        },
        "max_steps": 10,
    },

    "full-inbox-manager": {
        "name": "full-inbox-manager",
        "display_name": "Full Inbox Manager",
        "difficulty": "hard",
        "description": (
            "Manage a complete inbox of 15 emails. "
            "Categorize, prioritize, draft responses for emails that need them, "
            "and unsubscribe from unwanted senders. "
            "Response quality is scored by rubric (greeting, relevance, closing, length)."
        ),
        "email_ids": [
            "work_002",       # CRITICAL server — needs response
            "work_003",       # client complaint — needs response
            "important_003",  # legal notice — needs response
            "personal_002",   # mom RSVP — needs response
            "work_005",       # support ticket — needs response
            "important_001",  # lab results
            "important_002",  # Google interview
            "work_001",       # project update
            "work_004",       # HR reminder
            "personal_001",   # friend BBQ
            "newsletter_001", # TechCrunch
            "newsletter_002", # Medium
            "newsletter_003", # FashionHub promo — should unsubscribe
            "spam_001",       # lottery spam
            "spam_002",       # casino spam
        ],
        "scoring": {
            "category_weight": 0.30,
            "priority_weight": 0.30,
            "response_weight": 0.30,
            "unsubscribe_weight": 0.10,
        },
        "max_steps": 15,
    },
}


def get_task(task_name: str) -> Dict[str, Any]:
    if task_name not in TASK_CONFIGS:
        raise ValueError(f"Unknown task '{task_name}'. Valid tasks: {list(TASK_CONFIGS.keys())}")
    return TASK_CONFIGS[task_name]


def get_email(email_id: str) -> Dict[str, Any]:
    if email_id not in EMAILS:
        raise ValueError(f"Unknown email '{email_id}'")
    return EMAILS[email_id]


def get_task_emails(task_name: str) -> List[Dict[str, Any]]:
    task = get_task(task_name)
    return [EMAILS[eid] for eid in task["email_ids"]]
