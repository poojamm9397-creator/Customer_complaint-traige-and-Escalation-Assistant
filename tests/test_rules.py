from rules import apply_escalation_rules

def test_safety_overrides():
    result = apply_escalation_rules("safety_legal", [])
    assert result["priority"] == "P0"
    assert result["human_review_required"] is True

def test_urgent_case():
    result = apply_escalation_rules("course_access", ["urgent"])
    assert result["priority"] == "P1"
    assert result["queue"] == "Priority Support"
