from sqlalchemy import text


async def search_similar_chunks_dao(
    session,
    query_embedding: list[float],
    project_id: int,
    top_k: int = 3,
    threshold: float = 0.3,
) -> list[dict]:

    result = await session.execute(
        text("""
             SELECT
                 id,
                 contract_id,
                 chunk_index,
                 chunk_text,
                 1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
             FROM chunks
             WHERE project_id = :project_id
               AND 1 - (embedding <=> CAST(:embedding AS vector)) >= :threshold
             ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :top_k
             """),
        {
            "embedding": str(query_embedding),
            "project_id": project_id,
            "threshold": threshold,
            "top_k": top_k,
        },
    )

    rows = result.mappings().fetchall()
    return [
        {
            "id": row["id"],
            "contract_id": row["contract_id"],
            "chunk_index": row["chunk_index"],
            "text": row["chunk_text"],
            "similarity": round(row["similarity"], 4),
        }
        for row in rows
    ]
