-- Add exhibitors column to events table
-- This stores exhibitor information as JSON

ALTER TABLE events
ADD COLUMN IF NOT EXISTS exhibitors JSONB;

-- Add a comment to describe the column
COMMENT ON COLUMN events.exhibitors IS 'List of companies exhibiting at the event, stored as JSON with status and list fields';