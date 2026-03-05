-- V0.2 Schema: Add violation pattern detection fields
-- Adds support for intelligent violation pattern detection

-- Add violation pattern fields to case_intels table
ALTER TABLE case_intels ADD COLUMN violation_pattern TEXT DEFAULT 'unknown';
ALTER TABLE case_intels ADD COLUMN pattern_confidence REAL DEFAULT 0.0;
ALTER TABLE case_intels ADD COLUMN pattern_evidence TEXT;
ALTER TABLE case_intels ADD COLUMN monetary_amount TEXT;
ALTER TABLE case_intels ADD COLUMN monetary_value REAL;
ALTER TABLE case_intels ADD COLUMN quantity TEXT;
ALTER TABLE case_intels ADD COLUMN quantity_value REAL;
ALTER TABLE case_intels ADD COLUMN quantity_unit TEXT;
ALTER TABLE case_intels ADD COLUMN suspects TEXT;
ALTER TABLE case_intels ADD COLUMN brands TEXT;
ALTER TABLE case_intels ADD COLUMN vehicle_info TEXT;
ALTER TABLE case_intels ADD COLUMN risk_factors TEXT;
ALTER TABLE case_intels ADD COLUMN geographic_hints TEXT;

-- Create index for pattern queries
CREATE INDEX IF NOT EXISTS idx_case_intels_pattern ON case_intels(violation_pattern);
CREATE INDEX IF NOT EXISTS idx_case_intels_pattern_confidence ON case_intels(pattern_confidence);
CREATE INDEX IF NOT EXISTS idx_case_intels_monetary_value ON case_intels(monetary_value);

-- Create violation_pattern_stats view for analytics
CREATE VIEW IF NOT EXISTS violation_pattern_stats AS
SELECT 
    violation_pattern,
    COUNT(*) as total_cases,
    AVG(risk_score) as avg_risk_score,
    AVG(pattern_confidence) as avg_confidence,
    SUM(CASE WHEN risk_level = 'high' THEN 1 ELSE 0 END) as high_risk_count,
    SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed_count
FROM case_intels
WHERE is_case_related = 1
GROUP BY violation_pattern
ORDER BY total_cases DESC;