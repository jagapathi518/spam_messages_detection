-- Spam Shield: Supabase Database Schema
-- Run this migration in your Supabase SQL Editor

-- 1. Table: llm_cache (Caches Layer 3 Groq Second Opinions by SHA-256 hash)
CREATE TABLE IF NOT EXISTS public.llm_cache (
    message_hash VARCHAR(64) PRIMARY KEY,
    text_preview VARCHAR(120),
    label VARCHAR(20) NOT NULL,
    confidence NUMERIC(4, 3) NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for instant hash lookup
CREATE INDEX IF NOT EXISTS idx_llm_cache_hash ON public.llm_cache (message_hash);

-- 2. Table: scan_logs (Anonymous telemetry on scans for security dashboards)
CREATE TABLE IF NOT EXISTS public.scan_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text_preview VARCHAR(120) NOT NULL,
    label VARCHAR(20) NOT NULL,
    confidence NUMERIC(4, 3) NOT NULL,
    risk_score NUMERIC(4, 3) NOT NULL,
    layers_used TEXT[] NOT NULL,
    latency_ms NUMERIC(6, 2),
    user_id VARCHAR(64) DEFAULT 'anonymous',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_scan_logs_created_at ON public.scan_logs (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_scan_logs_label ON public.scan_logs (label);

-- 3. Table: user_feedback (User corrections to feed continuous learning retrain.py)
CREATE TABLE IF NOT EXISTS public.user_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text TEXT NOT NULL,
    predicted_label VARCHAR(20) NOT NULL,
    user_correction VARCHAR(20) NOT NULL,
    comments TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_feedback_verified ON public.user_feedback (is_verified);

-- Row Level Security (RLS)
ALTER TABLE public.llm_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scan_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_feedback ENABLE ROW LEVEL SECURITY;

-- Allow anonymous inserts and selects for client app
CREATE POLICY "Allow public read-write for llm_cache" ON public.llm_cache
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow public insert for scan_logs" ON public.scan_logs
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read for scan_logs" ON public.scan_logs
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert for user_feedback" ON public.user_feedback
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read for user_feedback" ON public.user_feedback
    FOR SELECT USING (true);
