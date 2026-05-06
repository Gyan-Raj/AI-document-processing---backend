# services/embedding_service.py

import asyncio
from sentence_transformers import SentenceTransformer
from db.connection import AsyncSessionLocal  # your existing DB setup
from utils.helper import extract_text  # reuse what you already have
from dao.embedding_and_chunks_dao import store_chunks_dao
from dao.contract_dao import update_contract_embedding_status_dao
from ai_models.model import get_model

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


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """Embed a list of text chunks. Returns list of 384-dim vectors."""
    model = get_model()  # loads on first call, cached after
    return model.encode(chunks, show_progress_bar=False).tolist()


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

            result = await update_contract_embedding_status_dao(
                session, user_id, project_id, contract_id, "processing"
            )
            print(result, "resultttttttttt")

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
        embeddings = await asyncio.get_event_loop().run_in_executor(
            None, embed_chunks, chunks
        )

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
