CREATE TABLE IF NOT EXISTS tickets (
    ticket_id           TEXT PRIMARY KEY,
    created_at          DATETIME NOT NULL,
    resolved_at         DATETIME,
    first_response_at   DATETIME,
    category            TEXT,
    subcategory         TEXT,
    priority            TEXT CHECK (priority IN ('Critical','High','Medium','Low')),
    status              TEXT,
    channel             TEXT,
    agent_id            TEXT,
    agent_name          TEXT,
    team                TEXT,
    customer_id         TEXT,
    customer_tier       TEXT,
    subject             TEXT,
    description         TEXT,
    tags                TEXT,
    csat_score          INTEGER CHECK (csat_score BETWEEN 1 AND 5),
    resolution_notes    TEXT,
    is_escalated        BOOLEAN DEFAULT 0,
    reopen_count        INTEGER DEFAULT 0,
    num_interactions    INTEGER DEFAULT 1,
    created_ts          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agent_metrics (
    metric_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id            TEXT NOT NULL,
    period              TEXT NOT NULL,
    tickets_handled     INTEGER,
    avg_resolution_hrs  REAL,
    sla_rate            REAL,
    avg_csat            REAL,
    escalation_rate     REAL,
    UNIQUE(agent_id, period)
);

CREATE TABLE IF NOT EXISTS sla_tracking (
    sla_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id           TEXT REFERENCES tickets(ticket_id),
    priority            TEXT,
    sla_target_hours    REAL,
    actual_hours        REAL,
    sla_met             BOOLEAN,
    breach_hours        REAL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_tickets_created ON tickets(created_at);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_category ON tickets(category);
CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority);
CREATE INDEX IF NOT EXISTS idx_tickets_agent ON tickets(agent_id);
CREATE INDEX IF NOT EXISTS idx_tickets_channel ON tickets(channel);
CREATE INDEX IF NOT EXISTS idx_sla_ticket ON sla_tracking(ticket_id);
