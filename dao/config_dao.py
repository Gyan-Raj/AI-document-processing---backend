from sqlalchemy import text


async def add_config_path_dao(
    session, user_id, project_id, folder_name, file_name, file_path
):
    insert_query = text("""
        INSERT INTO configs (user_id, project_id, config_path, config_name, folder_name) 
        VALUES (:user_id, :project_id, :file_path, :file_name, :folder_name)
        RETURNING id, user_id, project_id, config_path, config_name, folder_name
    """)
    result = await session.execute(
        insert_query,
        {
            "user_id": user_id,
            "project_id": project_id,
            "file_path": file_path,
            "file_name": file_name,
            "folder_name": folder_name,
        },
    )
    config_row = result.mappings().one()
    return config_row


async def get_config_path_dao(session, project_id):
    query = text("""
        SELECT * FROM configs WHERE project_id= :project_id
    """)
    result = await session.execute(query, {"project_id": project_id})
    return result.mappings().all()


async def get_config_path_by_doc_id_dao(session, doc_id):
    query = text("""
        SELECT * FROM configs WHERE id= :doc_id
    """)
    result = await session.execute(query, {"doc_id": doc_id})
    return result.mappings().first()


async def delete_config_path_dao(session, doc_id):
    query = text("""
        DELETE FROM configs WHERE id= :doc_id
    """)
    await session.execute(query, {"doc_id": doc_id})
