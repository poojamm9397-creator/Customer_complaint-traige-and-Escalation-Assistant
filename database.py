import os, json, sqlite3
from datetime import datetime, timezone
from config import get_settings

def _connect():
    path = get_settings().database_path
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = f.read()
    with _connect() as conn:
        conn.executescript(schema)

def create_complaint_and_customer(customer_ref, complaint_text, source_channel):
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO customers(external_ref, display_name, created_at) VALUES (?, ?, ?)",
            (customer_ref, customer_ref, now)
        )
        customer = conn.execute("SELECT customer_id FROM customers WHERE external_ref = ?", (customer_ref,)).fetchone()
        cur = conn.execute(
            """INSERT INTO complaints(customer_id, source_channel, original_text, received_at, status)
               VALUES (?, ?, ?, ?, ?)""",
            (customer["customer_id"], source_channel, complaint_text, now, "received")
        )
        complaint_id = cur.lastrowid
        conn.execute(
            "INSERT INTO complaint_messages(complaint_id, sender_type, message_text, created_at) VALUES (?, ?, ?, ?)",
            (complaint_id, "customer", complaint_text, now)
        )
        return complaint_id

def save_case(complaint_id, result, llm_result):
    now = datetime.now(timezone.utc).isoformat()
    case_id = f"CASE-{complaint_id:06d}"
    with _connect() as conn:
        conn.execute(
            """INSERT INTO cases(
                case_id, complaint_id, category, product_course_entity, sentiment,
                urgency_phrases_json, priority, recommended_queue, llm_summary,
                llm_rationale, llm_provider, llm_model, prompt_version, llm_status,
                human_review_required, review_status, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (case_id, complaint_id, result["category"], result.get("product_course_entity"),
             result["sentiment"], json.dumps(result["urgency_phrases"]), result["priority"],
             result["recommended_queue"], llm_result["summary"], llm_result["rationale"],
             llm_result["provider"], llm_result["model"], "1.0", llm_result["status"],
             int(result["human_review_required"]), "pending", "open", now, now)
        )
        conn.execute(
            """INSERT INTO triage_logs(complaint_id, stage, input_json, output_json, outcome, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (complaint_id, "triage_complete", "{}", json.dumps(result), "success", now)
        )
    return case_id

def log_error(complaint_id, stage, error):
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            """INSERT INTO triage_logs(complaint_id, stage, input_json, output_json, outcome, error_code, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (complaint_id, stage, "{}", "{}", "error", str(error)[:200], now)
        )

def list_cases(limit=100):
    with _connect() as conn:
        rows = conn.execute(
            """SELECT cs.case_id, cs.category, cs.priority, cs.recommended_queue,
                      cs.review_status, cs.status, cs.created_at
               FROM cases cs ORDER BY cs.created_at DESC LIMIT ?""", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

def get_case(case_id):
    with _connect() as conn:
        row = conn.execute(
            """SELECT cs.*, c.original_text FROM cases cs
               JOIN complaints c ON c.complaint_id = cs.complaint_id
               WHERE cs.case_id = ?""", (case_id,)
        ).fetchone()
        return dict(row) if row else None

def update_review(case_id, review_status, reviewer, notes):
    allowed = {"pending", "approved", "needs_follow_up", "rejected"}
    if review_status not in allowed:
        raise ValueError("Invalid review status.")
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            """UPDATE cases SET review_status=?, reviewer=?, review_notes=?,
               reviewed_at=?, updated_at=? WHERE case_id=?""",
            (review_status, reviewer.strip(), notes.strip(), now, now, case_id)
        )
        conn.execute(
            """INSERT INTO triage_logs(complaint_id, stage, input_json, output_json, outcome, created_at)
               SELECT complaint_id, 'human_review', '{}', ?, 'success', ? FROM cases WHERE case_id=?""",
            (json.dumps({"review_status": review_status, "reviewer": reviewer, "notes": notes}), now, case_id)
        )
