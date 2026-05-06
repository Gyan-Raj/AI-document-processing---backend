from db.connection import AsyncSessionLocal
from dao.contract_dao import (
    add_contract_path_dao,
    get_contract_dao,
    get_contract_by_doc_id_dao,
    delete_contract_dao,
)


async def add_contract_path(user_id, project_id, folder_name, file_name, file_path):
    async with AsyncSessionLocal() as session:
        contract = await add_contract_path_dao(
            session, user_id, project_id, folder_name, file_name, file_path
        )
        await session.commit()
        return contract


async def get_contract_path(session, project_id):
    contract_path = await get_contract_dao(session, project_id)
    await session.commit()
    return contract_path


async def get_contract_path_by_doc_id(session, doc_id):
    contract_path = await get_contract_by_doc_id_dao(session, doc_id)
    return contract_path


async def delete_contract_path(session, doc_id):
    await delete_contract_dao(session, doc_id)
