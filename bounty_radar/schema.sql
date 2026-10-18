PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS repos (
    full_name TEXT PRIMARY KEY,
    owner TEXT NOT NULL,
    name TEXT NOT NULL,
    html_url TEXT,
    description TEXT,
    default_branch TEXT,
    archived INTEGER NOT NULL DEFAULT 0,
    pushed_at TEXT,
    last_seen_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS repo_state (
    repo_full_name TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (repo_full_name, key),
    FOREIGN KEY (repo_full_name) REFERENCES repos(full_name)
);

CREATE TABLE IF NOT EXISTS repo_scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_full_name TEXT NOT NULL,
    scanned_at TEXT NOT NULL,
    heat_score INTEGER NOT NULL,
    previous_heat_score INTEGER,
    score_delta INTEGER NOT NULL,
    commit_count_24h INTEGER NOT NULL,
    baseline_commit_count INTEGER NOT NULL,
    velocity_multiplier REAL NOT NULL,
    summary_json TEXT NOT NULL,
    FOREIGN KEY (repo_full_name) REFERENCES repos(full_name)
);

CREATE INDEX IF NOT EXISTS idx_repo_scans_repo_time
ON repo_scans(repo_full_name, scanned_at);

CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_full_name TEXT NOT NULL,
    fingerprint TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    signal_key TEXT NOT NULL,
    severity INTEGER NOT NULL,
    title TEXT NOT NULL,
    details TEXT NOT NULL,
    url TEXT,
    metadata_json TEXT NOT NULL,
    first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    occurrences INTEGER NOT NULL DEFAULT 1,
    UNIQUE(repo_full_name, fingerprint),
    FOREIGN KEY (repo_full_name) REFERENCES repos(full_name)
);

CREATE TABLE IF NOT EXISTS scan_signals (
    scan_id INTEGER NOT NULL,
    signal_id INTEGER NOT NULL,
    is_new INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (scan_id, signal_id),
    FOREIGN KEY (scan_id) REFERENCES repo_scans(id),
    FOREIGN KEY (signal_id) REFERENCES signals(id)
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_full_name TEXT NOT NULL,
    scan_id INTEGER NOT NULL,
    alert_type TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    sent_at TEXT NOT NULL,
    FOREIGN KEY (repo_full_name) REFERENCES repos(full_name),
    FOREIGN KEY (scan_id) REFERENCES repo_scans(id)
);

CREATE TABLE IF NOT EXISTS sources (
    name TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    kind TEXT NOT NULL,
    last_seen_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS source_state (
    source_name TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (source_name, key),
    FOREIGN KEY (source_name) REFERENCES sources(name)
);

CREATE TABLE IF NOT EXISTS source_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL,
    fingerprint TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    signal_key TEXT NOT NULL,
    severity INTEGER NOT NULL,
    title TEXT NOT NULL,
    details TEXT NOT NULL,
    url TEXT,
    metadata_json TEXT NOT NULL,
    first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    occurrences INTEGER NOT NULL DEFAULT 1,
    UNIQUE(source_name, fingerprint),
    FOREIGN KEY (source_name) REFERENCES sources(name)
);

CREATE TABLE IF NOT EXISTS source_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    sent_at TEXT NOT NULL,
    FOREIGN KEY (source_name) REFERENCES sources(name)
);

CREATE TABLE IF NOT EXISTS telegram_outbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dedupe_key TEXT NOT NULL UNIQUE,
    alert_type TEXT NOT NULL,
    entity_name TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    last_attempt_at TEXT,
    last_error TEXT,
    sent_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_telegram_outbox_pending
ON telegram_outbox(sent_at, created_at);

CREATE TABLE IF NOT EXISTS source_item_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL,
    item_fingerprint TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    snapshot_json TEXT NOT NULL,
    observed_at TEXT NOT NULL,
    UNIQUE(source_name, item_fingerprint, content_hash),
    FOREIGN KEY (source_name) REFERENCES sources(name)
);

CREATE INDEX IF NOT EXISTS idx_source_item_snapshots_item_time
ON source_item_snapshots(source_name, item_fingerprint, observed_at);

CREATE TABLE IF NOT EXISTS source_item_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL,
    item_fingerprint TEXT NOT NULL,
    change_fingerprint TEXT NOT NULL,
    change_types_json TEXT NOT NULL,
    previous_snapshot_json TEXT NOT NULL,
    current_snapshot_json TEXT NOT NULL,
    detected_at TEXT NOT NULL,
    UNIQUE(source_name, change_fingerprint),
    FOREIGN KEY (source_name) REFERENCES sources(name)
);
