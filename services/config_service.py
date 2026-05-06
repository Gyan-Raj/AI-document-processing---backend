from db.connection import AsyncSessionLocal
from dao.config_dao import (
    add_config_path_dao,
    get_config_path_dao,
    get_config_path_by_doc_id_dao,
    delete_config_path_dao,
)


async def add_config_path(user_id, project_id, folder_name, file_name, file_path):
    async with AsyncSessionLocal() as session:
        config = await add_config_path_dao(
            session, user_id, project_id, folder_name, file_name, file_path
        )
        await session.commit()
        return config


async def get_config_path(session, project_id):
    config_path = await get_config_path_dao(session, project_id)
    await session.commit()
    return config_path


async def get_config_path_by_doc_id(session, doc_id):
    config_path = await get_config_path_by_doc_id_dao(session, doc_id)
    return config_path


async def delete_config_path(session, doc_id):
    await delete_config_path_dao(session, doc_id)
