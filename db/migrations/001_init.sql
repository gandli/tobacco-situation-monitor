-- V0.1 Database Schema Init
-- Creates core tables for OSINT pipeline

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    list_url TEXT NOT NULL,
    last_crawled_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS raw_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    url TEXT NOT NULL UNIQUE,
    title TEXT,
    published_at TEXT,
    content_raw TEXT,
    content_clean TEXT,
    url_hash TEXT,
    content_hash TEXT,
    fetched_at TEXT DEFAULT (datetime('now')),
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

CREATE TABLE IF NOT EXISTS case_intels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    is_case_related INTEGER DEFAULT 0,
    case_type TEXT,
    region TEXT,
    risk_score INTEGER DEFAULT 0,
    risk_level TEXT DEFAULT 'low',
    keywords_matched TEXT,
    status TEXT DEFAULT 'new',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (article_id) REFERENCES raw_articles(id)
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intel_id INTEGER NOT NULL,
    alert_type TEXT,
    message TEXT,
    is_sent INTEGER DEFAULT 0,
    sent_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (intel_id) REFERENCES case_intels(id)
);

CREATE TABLE IF NOT EXISTS review_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intel_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    comment TEXT,
    reviewed_at TEXT DEFAULT (datetime('now')),
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (intel_id) REFERENCES case_intels(id)
);