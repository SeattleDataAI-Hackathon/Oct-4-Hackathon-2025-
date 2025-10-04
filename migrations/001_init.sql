-- Users are identified only by WhatsApp number; don't store names/PHI
CREATE TABLE IF NOT EXISTS uploads (
  id BIGSERIAL PRIMARY KEY,
  user_phone TEXT NOT NULL,
  media_url TEXT,
  received_at TIMESTAMPTZ DEFAULT now(),
  ai_result JSONB,
  quality JSONB,
  triage_bucket TEXT,     -- e.g., 'unclear', 'concerning', 'non_specific'
  disclaimer_shown BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_uploads_user_phone ON uploads(user_phone);
CREATE INDEX IF NOT EXISTS idx_uploads_received_at ON uploads(received_at DESC);
