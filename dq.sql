-- Step 1: Enable pgvector extension (do this first, only once)
CREATE EXTENSION IF NOT EXISTS vector;

-- Step 2: Users table
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    user_name       VARCHAR(100),
    user_email      VARCHAR(100) NOT NULL UNIQUE,
    user_password   VARCHAR(255) NOT NULL,
    refresh_token   VARCHAR(255),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 3: Projects table
CREATE TABLE projects (
    id              SERIAL PRIMARY KEY,
    user_id         INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_name    VARCHAR(100),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 4: Contracts table
CREATE TABLE contracts (
    id              SERIAL PRIMARY KEY,
    user_id         INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id      INT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    contract_path   VARCHAR(255),
    folder_name     VARCHAR(255),
    contract_name   VARCHAR(255),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 5: Configs table
CREATE TABLE configs (
    id              SERIAL PRIMARY KEY,
    user_id         INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id      INT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    config_path     VARCHAR(255),
    folder_name     VARCHAR(255),
    config_name     VARCHAR(255),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 6: Risk summaries table
CREATE TABLE risk_summaries (
    id                  SERIAL PRIMARY KEY,
    user_id             INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id          INT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    risk_summary_path   VARCHAR(255),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 7: Chunks table (new — for RAG)
CREATE TABLE chunks (
    id              SERIAL PRIMARY KEY,
    user_id         INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id      INT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    contract_id     INT NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    chunk_index     INT NOT NULL,
    chunk_text      TEXT NOT NULL,
    embedding       vector(384),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 8: Index for fast similarity search
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);

-- Step 9: Index for fast lookup by contract
CREATE INDEX ON chunks (contract_id);

SELECT * FROM pg_extension WHERE extname = 'vector';