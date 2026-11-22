import re
from models import NLPResult

CATEGORY_TERMS = {
    "billing_refund": ["refund", "payment", "charged", "billing", "invoice", "duplicate charge"],
    "course_access": ["login", "log in", "cannot access", "can't access", "course access", "enrollment", "password"],
    "technical_issue": ["error", "crash", "not loading", "broken", "upload failed", "bug", "technical"],
    "content_quality": ["incorrect lesson", "wrong answer", "missing content", "outdated", "course material"],
    "instructor_support": ["instructor", "trainer", "teacher", "class support"],
    "certificate": ["certificate", "certification", "completion proof"],
    "safety_legal": ["safety", "threat", "harassment", "legal notice", "lawyer", "danger", "injury"],
}
URGENCY_TERMS = [
    "urgent", "immediately", "right now", "today", "due today", "deadline",
    "cannot continue", "can't continue", "safety risk", "legal notice", "threat"
]
POSITIVE_TERMS = ["thank you", "great", "excellent", "happy", "appreciate", "good service"]
NEGATIVE_TERMS = ["angry", "disappointed", "frustrated", "bad", "terrible", "unable", "cannot", "can't", "issue", "problem"]

def _contains(text: str, term: str) -> bool:
    return term in text

def analyze_text(text: str) -> NLPResult:
    normalized = re.sub(r"\s+", " ", text.lower()).strip()
    scores = {category: sum(1 for term in terms if _contains(normalized, term))
              for category, terms in CATEGORY_TERMS.items()}
    category = max(scores, key=scores.get) if max(scores.values(), default=0) else "other"
    urgency = [term for term in URGENCY_TERMS if _contains(normalized, term)]
    positive = sum(1 for term in POSITIVE_TERMS if _contains(normalized, term))
    negative = sum(1 for term in NEGATIVE_TERMS if _contains(normalized, term))
    sentiment = "positive" if positive > negative else "negative" if negative > positive else "neutral"

    # Lightweight entity extraction: capture a phrase following "course" where possible.
    entity = None
    match = re.search(r"\b(?:course|program|programme)\s+(?:on\s+)?([A-Z][A-Za-z0-9& -]{1,50})", text)
    if match:
        entity = match.group(1).strip(" .,!?:;")
    return NLPResult(category, entity, sentiment, urgency)
