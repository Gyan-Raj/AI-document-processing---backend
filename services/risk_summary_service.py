from db.connection import AsyncSessionLocal
from dao.risk_summary_path_dao import (
    add_risk_summary_path_dao,
    get_risk_summary_path_dao,
)


async def add_risk_summary_path(user_id, project_id, file_path):
    async with AsyncSessionLocal() as session:
        risk_summary = await add_risk_summary_path_dao(
            session, user_id, project_id, file_path
        )
        await session.commit()
        return risk_summary


async def get_risk_summary_path(session, project_id):
    contract_path = await get_risk_summary_path_dao(session, project_id)
    await session.commit()
    return contract_path
