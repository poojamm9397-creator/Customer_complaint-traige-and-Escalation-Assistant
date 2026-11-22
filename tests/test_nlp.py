from nlp import analyze_text

def test_course_access_and_urgency():
    result = analyze_text("I cannot log in to my course. My assessment is due today.")
    assert result.category == "course_access"
    assert "due today" in result.urgency_phrases

def test_safety_category():
    result = analyze_text("There is a safety risk and I need help.")
    assert result.category == "safety_legal"
