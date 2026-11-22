from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class NLPResult:
    category: str
    product_course_entity: str | None
    sentiment: str
    urgency_phrases: list[str]

@dataclass
class LLMResult:
    summary: str
    recommended_queue: str
    rationale: str
    uncertainties: list[str]
    provider: str
    model: str
    status: str

@dataclass
class TriageResult:
    complaint_id: int
    case_id: str
    category: str
    product_course_entity: str | None
    sentiment: str
    urgency_phrases: list[str]
    priority: str
    recommended_queue: str
    llm_summary: str
    llm_rationale: str
    llm_provider: str
    llm_model: str
    llm_status: str
    human_review_required: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
