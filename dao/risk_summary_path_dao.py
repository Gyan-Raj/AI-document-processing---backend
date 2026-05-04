from sqlalchemy import text


async def add_risk_summary_path_dao(session, user_id, project_id, file_path):
    insert_query = text("""
        INSERT INTO risk_summaries (user_id, project_id, risk_summary_path) 
        VALUES (:user_id, :project_id, :risk_summary_path)
    """)
    await session.execute(
        insert_query,
        {
            "user_id": user_id,
            "project_id": project_id,
            "risk_summary_path": file_path,
        },
    )


async def get_risk_summary_path_dao(session, project_id):
    query = text("""
        SELECT * FROM risk_summaries WHERE project_id= :project_id ORDER BY created_at DESC
    """)
    result = await session.execute(query, {"project_id": project_id})
    return result.mappings().all()


async def get_risk_summary_path_by_doc_id_dao(session, doc_id):
    query = text("""
        SELECT * FROM risk_summaries WHERE id= :doc_id
    """)
    result = await session.execute(query, {"doc_id": doc_id})
    return result.mappings().first()
