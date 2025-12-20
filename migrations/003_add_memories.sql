-- Migration: Add memories table for long-term memory
-- Description: Store important information, preferences, and decisions

CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_type TEXT NOT NULL,  -- 'preference', 'decision', 'fact', 'context'
    content TEXT NOT NULL,
    project_id INTEGER,  -- NULL for global memories
    importance INTEGER DEFAULT 5,  -- 1-10 scale (10 = critical)
    tags TEXT,  -- JSON array of tags for better retrieval
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Index for faster retrieval
CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_memories_project ON memories(project_id);
CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance);
CREATE INDEX IF NOT EXISTS idx_memories_accessed ON memories(last_accessed);

-- Add some initial memories about Master Christian
INSERT INTO memories (memory_type, content, importance, tags) VALUES
('preference', 'Master Christian prefers proactive agents that take initiative without asking for confirmation', 10, '["personality", "workflow"]'),
('fact', 'Master Christian uses Albedo, Dev Agent (StreamUI), and Lead Dev Agent (Claude Sonnet 4.5) as his development team', 10, '["team", "agents"]'),
('preference', 'Master Christian likes agents to use StreamUI framework for fast, efficient code generation', 9, '["technology", "streamui"]'),
('fact', 'Dev Agent uses GPT-4o and is 76% faster than LangGraph with 66% fewer tokens', 8, '["performance", "dev-agent"]');
