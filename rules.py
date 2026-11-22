CATEGORY_QUEUES = {
    "billing_refund": "Billing Support",
    "course_access": "Learning Support",
    "technical_issue": "Technical Support",
    "content_quality": "Content Review",
    "instructor_support": "Instructor Support",
    "certificate": "Certification Support",
    "safety_legal": "Trust & Safety",
    "other": "General Support",
}

def apply_escalation_rules(category: str, urgency_phrases: list[str]) -> dict:
    # Safety/legal issues always take precedence and require a human.
    if category == "safety_legal" or any(p in urgency_phrases for p in ["safety risk", "legal notice", "threat"]):
        return {"priority": "P0", "queue": "Trust & Safety", "human_review_required": True}
    if any(p in urgency_phrases for p in ["urgent", "immediately", "right now", "today", "due today", "deadline"]):
        return {"priority": "P1", "queue": "Priority Support", "human_review_required": True}
    priority = "P3" if category == "other" else "P2"
    return {
        "priority": priority,
        "queue": CATEGORY_QUEUES.get(category, "General Support"),
        "human_review_required": False
    }
