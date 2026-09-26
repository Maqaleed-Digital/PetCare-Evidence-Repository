-- 0051 · NFR-15 API rate limiting (MVC-BUILD-RUNNER-001 v1.2 U24)
--
-- One row per (bucket, minute window); every worker and process increments the same row atomically
-- (INSERT … ON CONFLICT DO UPDATE … RETURNING), so the count is shared across the deployment. Buckets are
-- 'principal:<user_id>' (from the validated session) or 'ip:<client ip>'. Additive only.

CREATE TABLE IF NOT EXISTS rate_limit_counter (
    bucket TEXT NOT NULL CHECK (length(TRIM(bucket)) > 0),
    window_start BIGINT NOT NULL,
    count INTEGER NOT NULL CHECK (count > 0),
    PRIMARY KEY (bucket, window_start)
);
