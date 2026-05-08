# services/embedding_service.py

import asyncio
from db.connection import AsyncSessionLocal  # your existing DB setup
from utils.embedding_and_chunk import extract_text  # reuse what you already have
from dao.embedding_and_chunks_dao import store_chunks_dao
from dao.contract_dao import update_contract_embedding_status_dao
from utils.embedding_and_chunk import embed_query, embed_chunks
from dao.chunks_dao import search_similar_chunks_dao

# Load model once at module level — not inside the function
# This is important: loading takes ~2 seconds, you don't want it per request

CHUNK_SIZE = 500
# CHUNK_SIZE = 300
OVERLAP = 50
# OVERLAP = 30


def chunk_text(
    text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP
) -> list[str]:
    """Your function from session 4 — paste it here."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


async def embed_and_store_chunks(
    user_id: int, project_id: int, contract_id: int, contract_path: str
) -> int:
    """
    Full pipeline: PDF → chunks → embeddings → stored in DB.
    Returns number of chunks stored.
    Called once per contract, at upload time.
    """
    try:
        async with AsyncSessionLocal() as session:
            print("changed to processing")

            await update_contract_embedding_status_dao(
                session, user_id, project_id, contract_id, "processing"
            )

        # Step 1 — extract text (reusing your existing function)
        text = extract_text(contract_path)
        if not text.strip():
            print(f"Warning: no text extracted from {contract_path}")
            return 0

        # Step 2 — chunk
        chunks = chunk_text(text)
        if not chunks:
            return 0

        # Step 3 — embed (CPU-bound — run in executor so it doesn't block async event loop)
        embeddings = await embed_chunks(chunks)

        # Step 4 — store in DB
        async with AsyncSessionLocal() as session:
            await store_chunks_dao(
                session, user_id, project_id, contract_id, chunks, embeddings
            )
        print(f"Stored {len(chunks)} chunks for contract_id={contract_id}")
        async with AsyncSessionLocal() as session:
            await update_contract_embedding_status_dao(
                session, user_id, project_id, contract_id, "completed"
            )
        return len(chunks)
    except Exception as e:
        print(f"Embedding failed for contract_id={contract_id}: {e}")
        async with AsyncSessionLocal() as session:
            await update_contract_embedding_status_dao(
                session, user_id, project_id, contract_id, "failed"
            )


async def retrieve_context_for_config(
    project_id: int, config_rows: list, top_k: int = 1, threshold: float = 0.3
) -> str:
    sections = []

    for row in config_rows:
        if str(row.get("Enabled", "Yes")).strip().lower() != "yes":
            continue

        query = (row.get("Keywords") or row.get("Subject") or "").strip()
        if not query:
            continue

        query_embedding = await embed_query(query)

        async with AsyncSessionLocal() as session:
            chunks = await search_similar_chunks_dao(
                session, query_embedding, project_id, top_k=top_k, threshold=threshold
            )

        # debug — remove after tuning
        print(f"\n--- Query: {query} ---")
        for c in chunks:
            print(f"  similarity: {c['similarity']} | chunk: {c['text'][:150]}")

        if not chunks:
            continue

        chunk_texts = "\n---\n".join(c["text"] for c in chunks)
        sections.append(f"[Subject: {row['Subject']}]\n{chunk_texts}")

    return "\n\n===\n\n".join(sections)
