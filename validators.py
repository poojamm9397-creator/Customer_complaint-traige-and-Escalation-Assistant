from config import get_settings

def validate_complaint(customer_ref: str, complaint_text: str) -> tuple[str, str]:
    customer_ref = (customer_ref or "").strip()
    complaint_text = (complaint_text or "").strip()
    if not customer_ref:
        raise ValueError("Customer reference is required.")
    if not complaint_text:
        raise ValueError("Complaint text is required.")
    max_chars = get_settings().max_complaint_chars
    if len(complaint_text) > max_chars:
        raise ValueError(f"Complaint is too long. Maximum allowed length is {max_chars} characters.")
    return customer_ref, complaint_text
