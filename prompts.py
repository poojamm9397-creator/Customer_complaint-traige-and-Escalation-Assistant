PROMPT_VERSION = "1.0"

SYSTEM_PROMPT = """You prepare neutral internal summaries of customer complaints.
Use only the supplied information. Do not invent facts, assign blame, make legal
conclusions, promise outcomes, or take actions. The application's deterministic
rules control priority and human-review requirements; never change them.
Return only a JSON object with keys: summary, recommended_queue, rationale,
uncertainties. Do not include markdown fences."""

def build_user_prompt(complaint_text: str, nlp: dict, rules: dict) -> str:
    return f"""Complaint:
{complaint_text}

NLP findings:
{nlp}

Application escalation decision:
{rules}

Create a concise neutral summary and explain the queue recommendation.
Do not change the priority or human-review decision. Return the requested JSON."""
