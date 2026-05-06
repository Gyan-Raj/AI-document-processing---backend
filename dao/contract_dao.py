from sqlalchemy import text


async def add_contract_path_dao(
    session, user_id, project_id, folder_name, file_name, file_path
):
    insert_query = text("""
        INSERT INTO contracts (user_id, project_id, contract_path, contract_name, folder_name) 
        VALUES (:user_id, :project_id, :file_path, :file_name, :folder_name)
        RETURNING id, user_id, project_id, contract_path, contract_name, folder_name
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
    contract_row = result.mappings().one()
    return contract_row


async def get_contract_dao(session, project_id):
    query = text("""
        SELECT * FROM contracts WHERE project_id= :project_id
    """)
    result = await session.execute(query, {"project_id": project_id})
    return result.mappings().all()


async def get_contract_by_doc_id_dao(session, doc_id):
    query = text("""
        SELECT * FROM contracts WHERE id= :doc_id
    """)
    result = await session.execute(query, {"doc_id": doc_id})
    return result.mappings().first()


async def delete_contract_dao(session, doc_id):
    query = text("""
        DELETE FROM contracts WHERE id= :doc_id
    """)
    await session.execute(query, {"doc_id": doc_id})


async def update_contract_embedding_status_dao(
    session, user_id, project_id, document_id, status
):
    update_query = text("""
        UPDATE contracts SET embedding_status = :status WHERE project_id = :project_id AND user_id = :user_id AND id= :document_id
        RETURNING id, user_id, project_id, embedding_status, created_at
    """)
    result = await session.execute(
        update_query,
        {
            "project_id": project_id,
            "user_id": user_id,
            "status": status,
            "document_id": document_id,
        },
    )

    project_row = result.mappings().one()
    await session.commit()
    return project_row
