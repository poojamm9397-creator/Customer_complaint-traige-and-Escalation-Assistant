from validators import validate_complaint
from nlp import analyze_text
from rules import apply_escalation_rules
from llm_client import LLMClient
from database import create_complaint_and_customer, save_case, log_error
from models import TriageResult

class TriageWorkflow:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or LLMClient()

    def process_complaint(self, customer_ref, complaint_text, source_channel="web"):
        customer_ref, complaint_text = validate_complaint(customer_ref, complaint_text)
        complaint_id = create_complaint_and_customer(customer_ref, complaint_text, source_channel)
        try:
            nlp = analyze_text(complaint_text)
            rule_result = apply_escalation_rules(nlp.category, nlp.urgency_phrases)
            llm_result = self.llm_client.summarize(
                complaint_text,
                {
                    "category": nlp.category,
                    "product_course_entity": nlp.product_course_entity,
                    "sentiment": nlp.sentiment,
                    "urgency_phrases": nlp.urgency_phrases,
                },
                rule_result,
            )
            result = {
                "category": nlp.category,
                "product_course_entity": nlp.product_course_entity,
                "sentiment": nlp.sentiment,
                "urgency_phrases": nlp.urgency_phrases,
                "priority": rule_result["priority"],
                "recommended_queue": rule_result["queue"],
                "human_review_required": rule_result["human_review_required"],
            }
            case_id = save_case(complaint_id, result, llm_result)
            return TriageResult(
                complaint_id=complaint_id, case_id=case_id,
                category=nlp.category, product_course_entity=nlp.product_course_entity,
                sentiment=nlp.sentiment, urgency_phrases=nlp.urgency_phrases,
                priority=rule_result["priority"], recommended_queue=rule_result["queue"],
                llm_summary=llm_result["summary"], llm_rationale=llm_result["rationale"],
                llm_provider=llm_result["provider"], llm_model=llm_result["model"],
                llm_status=llm_result["status"],
                human_review_required=rule_result["human_review_required"]
            ).to_dict()
        except Exception as exc:
            log_error(complaint_id, "workflow", exc)
            raise
