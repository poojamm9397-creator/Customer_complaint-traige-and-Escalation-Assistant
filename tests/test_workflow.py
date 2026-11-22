from workflow import TriageWorkflow

class FakeLLM:
    def summarize(self, complaint_text, nlp, rules):
        return {
            "summary": "Customer cannot access the course before a deadline.",
            "recommended_queue": rules["queue"],
            "rationale": "The complaint indicates a time-sensitive access issue.",
            "uncertainties": [],
            "provider": "mock-test",
            "model": "offline-fake",
            "status": "mock_test"
        }

def test_end_to_end_creates_case(isolated_db):
    workflow = TriageWorkflow(llm_client=FakeLLM())
    result = workflow.process_complaint(
        "SYNTH-100",
        "I cannot log in to the Data Analytics course. My assessment is due today.",
        "web"
    )
    assert result["case_id"].startswith("CASE-")
    assert result["category"] == "course_access"
    assert result["priority"] == "P1"
    assert result["llm_status"] == "mock_test"
