-- RealVibe Site Copilot - Initial Database Schema
-- Version: 1.0

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Sites Table: Stores information about each research site
CREATE TABLE IF NOT EXISTS sites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Files Table: Stores uploaded documents with metadata
CREATE TABLE IF NOT EXISTS files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    storage_path VARCHAR(1024) NOT NULL,
    upload_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Chunks Table: Stores text chunks with embeddings for search
CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID REFERENCES files(id) ON DELETE CASCADE,
    page_number INT,
    chunk_text TEXT NOT NULL,
    embedding VECTOR(1536), -- OpenAI's text-embedding-ada-002 has 1536 dimensions
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Answer Memory Table: Canonical answers with provenance
CREATE TABLE IF NOT EXISTS answer_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(id) ON DELETE CASCADE,
    question_hash VARCHAR(64) NOT NULL, -- SHA256 hash of the normalized question
    answer_value TEXT,
    evidence_file_id UUID REFERENCES files(id),
    evidence_page INT,
    evidence_span JSONB, -- To store text coordinates
    confidence_score FLOAT,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(site_id, question_hash)
);

-- 5. Questionnaire Templates Table: Sponsor questionnaire schemas
CREATE TABLE IF NOT EXISTS questionnaire_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sponsor_name VARCHAR(255),
    template_name VARCHAR(255) NOT NULL,
    schema_definition JSONB NOT NULL, -- To store the questionnaire structure
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Runs Table: Autofill execution records
CREATE TABLE IF NOT EXISTS runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(id) ON DELETE CASCADE,
    questionnaire_template_id UUID REFERENCES questionnaire_templates(id),
    start_time TIMESTAMPTZ DEFAULT NOW(),
    end_time TIMESTAMPTZ,
    status VARCHAR(50) DEFAULT 'in_progress', -- e.g., in_progress, completed, failed
    autofill_percentage FLOAT,
    review_time_minutes INT,
    cycle_time_delta_weeks FLOAT
);

-- 7. Answers Table: Individual field answers with evidence
CREATE TABLE IF NOT EXISTS answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES runs(id) ON DELETE CASCADE,
    question_field_id VARCHAR(255) NOT NULL,
    answer_value TEXT,
    confidence_score FLOAT,
    evidence_links JSONB, -- Array of {file_id, page, span}
    review_status VARCHAR(50) DEFAULT 'needs_review', -- e.g., needs_review, accepted, edited
    reviewer_comments TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_answer_memory_question_hash ON answer_memory(question_hash);

-- Row-Level Security Policies
ALTER TABLE sites ENABLE ROW LEVEL SECURITY;
ALTER TABLE files ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE answer_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE answers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Sites are viewable by users of the site" ON sites FOR SELECT USING (id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid);
CREATE POLICY "Files are viewable by users of the site" ON files FOR SELECT USING (site_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid);
CREATE POLICY "Chunks are viewable by users of the site" ON chunks FOR SELECT USING (file_id IN (SELECT id FROM files WHERE site_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid));
CREATE POLICY "Answer memory is viewable by users of the site" ON answer_memory FOR SELECT USING (site_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid);
CREATE POLICY "Runs are viewable by users of the site" ON runs FOR SELECT USING (site_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid);
CREATE POLICY "Answers are viewable by users of the site" ON answers FOR SELECT USING (run_id IN (SELECT id FROM runs WHERE site_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid));

CREATE POLICY "Users can insert into their own site's tables" ON sites FOR INSERT WITH CHECK (id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid);
CREATE POLICY "Users can insert into their own site's tables" ON files FOR INSERT WITH CHECK (site_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid);
CREATE POLICY "Users can insert into their own site's tables" ON chunks FOR INSERT WITH CHECK (file_id IN (SELECT id FROM files WHERE site_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid));
CREATE POLICY "Users can insert into their own site's tables" ON answer_memory FOR INSERT WITH CHECK (site_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid);
CREATE POLICY "Users can insert into their own site's tables" ON runs FOR INSERT WITH CHECK (site_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid);
CREATE POLICY "Users can insert into their own site's tables" ON answers FOR INSERT WITH CHECK (run_id IN (SELECT id FROM runs WHERE site_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid));

CREATE POLICY "Users can update their own site's data" ON sites FOR UPDATE USING (id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid);
CREATE POLICY "Users can update their own site's data" ON files FOR UPDATE USING (site_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid);
CREATE POLICY "Users can update their own site's data" ON chunks FOR UPDATE USING (file_id IN (SELECT id FROM files WHERE site_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid));
CREATE POLICY "Users can update their own site's data" ON answer_memory FOR UPDATE USING (site_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid);
CREATE POLICY "Users can update their own site's data" ON runs FOR UPDATE USING (site_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid);
CREATE POLICY "Users can update their own site's data" ON answers FOR UPDATE USING (run_id IN (SELECT id FROM runs WHERE site_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid));

CREATE POLICY "Users can delete their own site's data" ON sites FOR DELETE USING (id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid);
CREATE POLICY "Users can delete their own site's data" ON files FOR DELETE USING (site_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid);
CREATE POLICY "Users can delete their own site's data" ON chunks FOR DELETE USING (file_id IN (SELECT id FROM files WHERE site_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid));
CREATE POLICY "Users can delete their own site's data" ON answer_memory FOR DELETE USING (site_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid);
CREATE POLICY "Users can delete their own site's data" ON runs FOR DELETE USING (site_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid);
CREATE POLICY "Users can delete their own site's data" ON answers FOR DELETE USING (run_id IN (SELECT id FROM runs WHERE site_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'site_id')::uuid));


