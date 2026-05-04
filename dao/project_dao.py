from sqlalchemy import text


async def create_project_dao(session, projectName, user_id):
    insert_query = text("""
        INSERT INTO projects (project_name, user_id) 
        VALUES (:projectName, :userId)
        RETURNING id, project_name, user_id, created_at
    """)
    result = await session.execute(
        insert_query, {"projectName": projectName, "userId": user_id}
    )
    # project_id = result.lastrowid  # ✅ get inserted ID (mySQL)
    project_row = result.mappings().one()
    return project_row


async def delete_project_dao(session, project_id, user_id):
    delete_query = text("""
        DELETE FROM projects WHERE id= :project_id AND user_id = :user_id
    """)
    await session.execute(delete_query, {"project_id": project_id, "user_id": user_id})


async def get_project_details_dao(session, project_id, user_id):
    select_query = text("""
        SELECT * FROM projects WHERE id = :id AND user_id = :user_id
    """)
    project = await session.execute(
        select_query, {"id": project_id, "user_id": user_id}
    )
    project_row = project.mappings().first()
    return project_row


async def get_all_projects_dao(session, user_id, query: str = ""):
    if query:
        select_query = text("""
            SELECT * FROM projects
            WHERE user_id = :user_id
            AND (
                LOWER(project_name) LIKE LOWER(:query)
                OR CAST(id AS TEXT) LIKE :query
            )
            ORDER BY created_at DESC
        """)
        params = {"user_id": user_id, "query": f"%{query}%"}
    else:
        select_query = text("""
            SELECT * FROM projects
            WHERE user_id = :user_id
            ORDER BY created_at DESC
        """)
        params = {"user_id": user_id}

    result = await session.execute(select_query, params)
    return result.mappings().all()
