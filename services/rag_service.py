import asyncio
from db.connection import AsyncSessionLocal
from dao.chunks_dao import search_similar_chunks_dao
from ai_models.model import get_model


def embed_query(text: str) -> list[float]:
    model = get_model()
    return model.encode([text])[0].tolist()


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

        query_embedding = await asyncio.get_event_loop().run_in_executor(
            None, embed_query, query
        )

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
