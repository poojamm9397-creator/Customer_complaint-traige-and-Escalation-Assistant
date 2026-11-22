CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_ref TEXT NOT NULL UNIQUE,
    display_name TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS complaints (
    complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    source_channel TEXT NOT NULL,
    original_text TEXT NOT NULL,
    received_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'received',
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS complaint_messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    sender_type TEXT NOT NULL,
    message_text TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(complaint_id) REFERENCES complaints(complaint_id)
);

CREATE TABLE IF NOT EXISTS escalation_rules (
    rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_code TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    priority TEXT NOT NULL,
    queue_name TEXT NOT NULL,
    match_terms_json TEXT NOT NULL DEFAULT '[]',
    human_review_required INTEGER NOT NULL DEFAULT 0,
    enabled INTEGER NOT NULL DEFAULT 1,
    rule_version TEXT NOT NULL DEFAULT '1.0'
);

CREATE TABLE IF NOT EXISTS cases (
    case_id TEXT PRIMARY KEY,
    complaint_id INTEGER NOT NULL UNIQUE,
    category TEXT NOT NULL,
    product_course_entity TEXT,
    sentiment TEXT NOT NULL,
    urgency_phrases_json TEXT NOT NULL,
    priority TEXT NOT NULL,
    recommended_queue TEXT NOT NULL,
    llm_summary TEXT,
    llm_rationale TEXT,
    llm_provider TEXT,
    llm_model TEXT,
    prompt_version TEXT,
    llm_status TEXT,
    human_review_required INTEGER NOT NULL DEFAULT 0,
    review_status TEXT NOT NULL DEFAULT 'pending',
    reviewer TEXT,
    review_notes TEXT,
    reviewed_at TEXT,
    status TEXT NOT NULL DEFAULT 'open',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(complaint_id) REFERENCES complaints(complaint_id)
);

CREATE TABLE IF NOT EXISTS triage_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    stage TEXT NOT NULL,
    input_json TEXT,
    output_json TEXT,
    outcome TEXT NOT NULL,
    error_code TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(complaint_id) REFERENCES complaints(complaint_id)
);
