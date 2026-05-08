# dao/chunks_dao.py  (new file)

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def store_chunks_dao(
    session: AsyncSession,
    user_id: int,
    project_id: int,
    contract_id: int,
    chunks: list[str],
    embeddings: list[list[float]],
) -> None:
    await session.execute(
        text("DELETE FROM chunks WHERE contract_id = :contract_id"),
        {"contract_id": contract_id},
    )

    rows = [
        {
            "user_id": user_id,
            "project_id": project_id,
            "contract_id": contract_id,
            "chunk_index": i,
            "chunk_text": chunk,
            "embedding": str(embedding),
        }
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]

    await session.execute(
        text("""
            INSERT INTO chunks (user_id, project_id, contract_id, chunk_index, chunk_text, embedding)
            VALUES (:user_id, :project_id, :contract_id, :chunk_index, :chunk_text, :embedding)
        """),
        rows,  # SQLAlchemy sends this as a single batch
    )

    await session.commit()


async def search_similar_chunks_dao(
    session: AsyncSession,
    query_embedding: list[float],
    project_id: int,
    top_k: int = 5,
    threshold: float = 0.75,
) -> list[dict]:
    """Retrieve top-k chunks most similar to the query embedding."""

    result = await session.execute(
        text("""
            SELECT
                contract_id,
                chunk_index,
                chunk_text,
                1 - (embedding <=> :embedding ::vector) AS similarity
            FROM chunks
            WHERE project_id = :project_id
              AND 1 - (embedding <=> :embedding ::vector) >= :threshold
            ORDER BY embedding <=> :embedding ::vector
            LIMIT :top_k
        """),
        {
            "embedding": str(query_embedding),
            "project_id": project_id,
            "threshold": threshold,
            "top_k": top_k,
        },
    )

    rows = result.fetchall()
    return [
        {
            "contract_id": r[0],
            "chunk_index": r[1],
            "text": r[2],
            "similarity": round(r[3], 4),
        }
        for r in rows
    ]
