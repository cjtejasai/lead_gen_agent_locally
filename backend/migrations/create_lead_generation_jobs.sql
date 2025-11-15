-- Create lead_generation_jobs table
-- Tracks the status of lead generation agent runs

CREATE TABLE IF NOT EXISTS lead_generation_jobs (
    id SERIAL PRIMARY KEY,
    recording_id INTEGER NOT NULL REFERENCES recordings(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending' NOT NULL,
    leads_found INTEGER DEFAULT 0,
    error_message TEXT,
    email_sent BOOLEAN DEFAULT FALSE,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    -- Index for querying jobs by recording
    CONSTRAINT fk_recording FOREIGN KEY (recording_id) REFERENCES recordings(id) ON DELETE CASCADE
);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_lead_jobs_recording ON lead_generation_jobs(recording_id);
CREATE INDEX IF NOT EXISTS idx_lead_jobs_created ON lead_generation_jobs(created_at DESC);

-- Add comment
COMMENT ON TABLE lead_generation_jobs IS 'Tracks lead generation agent runs and their results';