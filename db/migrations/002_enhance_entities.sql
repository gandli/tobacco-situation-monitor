-- V0.2 Schema Enhancement: Add entities and alerts
-- Adds tables for extracted entities, alerts, and case associations

-- Add entity columns to case_intels
ALTER TABLE case_intels ADD COLUMN monetary_amount TEXT;
ALTER TABLE case_intels ADD COLUMN monetary_value REAL;
ALTER TABLE case_intels ADD COLUMN quantity TEXT;
ALTER TABLE case_intels ADD COLUMN quantity_value REAL;
ALTER TABLE case_intels ADD COLUMN quantity_unit TEXT;
ALTER TABLE case_intels ADD COLUMN suspects TEXT;
ALTER TABLE case_intels ADD COLUMN brands TEXT;
ALTER TABLE case_intels ADD COLUMN vehicle_info TEXT;
ALTER TABLE case_intels ADD COLUMN case_number TEXT;
ALTER TABLE case_intels ADD COLUMN entity_confidence REAL DEFAULT 0;

-- Update alerts table with more fields
ALTER TABLE alerts ADD COLUMN rule_name TEXT;
ALTER TABLE alerts ADD COLUMN severity TEXT DEFAULT 'warning';
ALTER TABLE alerts ADD COLUMN title TEXT;
ALTER TABLE alerts ADD COLUMN details TEXT;

-- Create case associations table for linking related cases
CREATE TABLE IF NOT EXISTS case_associations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intel_id_a INTEGER NOT NULL,
    intel_id_b INTEGER NOT NULL,
    association_type TEXT NOT NULL,  -- 'same_region', 'same_suspect', 'same_vehicle', 'temporal'
    confidence REAL DEFAULT 0,
    evidence TEXT,  -- JSON with supporting evidence
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (intel_id_a) REFERENCES case_intels(id),
    FOREIGN KEY (intel_id_b) REFERENCES case_intels(id),
    UNIQUE(intel_id_a, intel_id_b, association_type)
);

-- Create alert rules configuration table
CREATE TABLE IF NOT EXISTS alert_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    alert_type TEXT NOT NULL,
    severity TEXT DEFAULT 'warning',
    description TEXT,
    conditions TEXT,  -- JSON with rule conditions
    enabled INTEGER DEFAULT 1,
    cooldown_hours INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Create trend snapshots for historical tracking
CREATE TABLE IF NOT EXISTS trend_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_date TEXT NOT NULL,
    granularity TEXT NOT NULL,  -- 'day', 'week', 'month'
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    metrics TEXT,  -- JSON with trend metrics
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(snapshot_date, granularity)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_case_intels_region ON case_intels(region);
CREATE INDEX IF NOT EXISTS idx_case_intels_case_type ON case_intels(case_type);
CREATE INDEX IF NOT EXISTS idx_case_intels_risk_level ON case_intels(risk_level);
CREATE INDEX IF NOT EXISTS idx_case_intels_created_at ON case_intels(created_at);
CREATE INDEX IF NOT EXISTS idx_case_intels_monetary_value ON case_intels(monetary_value);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at);
CREATE INDEX IF NOT EXISTS idx_case_associations_intel_id ON case_associations(intel_id_a, intel_id_b);