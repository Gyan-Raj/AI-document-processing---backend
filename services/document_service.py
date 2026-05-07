import os
from services.contract_service import (
    add_contract_path,
    delete_contract_path,
    get_contract_path,
)
from services.config_service import add_config_path, delete_config_path
from services.embedding_and_chunks_service import embed_and_store_chunks
from dao.risk_summary_dao import get_risk_summary_path_by_doc_id_dao
from dao.contract_dao import get_contract_by_doc_id_dao
from dao.config_dao import get_config_path_by_doc_id_dao
from dao.contract_dao import update_contract_embedding_status_dao
import uuid
from db.connection import AsyncSessionLocal
from fastapi import HTTPException
from config.constants import UPLOAD_DIR, RISK_SUMMARY_DIR
from utils.cleanup_empty_dirs import cleanup_empty_dirs


async def upload_document(
    file, project_id, user_id, folder_name, file_type, file_name, background_tasks
):

    async with AsyncSessionLocal() as session:
        existing = await get_contract_path(session, project_id)

    # ✅ find existing folder
    folder = next(
        (exist for exist in existing if exist["folder_name"] == folder_name), None
    )
    base_path = f"{UPLOAD_DIR}/{user_id}/{project_id}"

    # ✅ reuse folder if exists
    if not folder and not folder_name and file_type == "config":
        folder_path = base_path
        print("Global config file")
    else:
        if folder:
            folder_path = os.path.dirname(folder["contract_path"])
        else:
            folder_path = f"{base_path}/Folder_{uuid.uuid4().hex}"
            os.makedirs(folder_path, exist_ok=True)

    # ✅ unique file name
    ext = os.path.splitext(file.filename)[1]
    file_id = uuid.uuid4().hex
    file_path = f"{folder_path}/{file_type}_{file_id}{ext}"

    # save file
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # DB save
    document_id = None
    if file_type == "config":
        document_id = await add_config_path(
            user_id, project_id, folder_name, file.filename, file_path
        )
    elif file_type == "contract":
        document_id = await add_contract_path(
            user_id, project_id, folder_name, file.filename, file_path
        )

        background_tasks.add_task(
            embed_and_store_chunks, user_id, project_id, document_id["id"], file_path
        )

    return document_id


async def delete_document(user_id, project_id, doc_id, doc_type):
    # DB operations
    folder_name = None
    async with AsyncSessionLocal() as session:
        if doc_type == "config":
            result = await get_config_path_by_doc_id_dao(session, doc_id)
            await delete_config_path(session, doc_id)
            file_path = result["config_path"]
            folder_name = result["folder_name"]
        elif doc_type == "contract":
            result = await get_contract_by_doc_id_dao(session, doc_id)
            await delete_contract_path(session, doc_id)
            file_path = result["contract_path"]
            folder_name = result["folder_name"]
        elif doc_type == "risk-assessment":
            result = await get_risk_summary_path_by_doc_id_dao(session, doc_id)
            await delete_contract_path(session, doc_id)
            file_path = result["risk_summary_path"]
            folder_name = result["folder_name"]
        else:
            raise HTTPException(status_code=400, detail="Invalid doc type")
        await session.commit()

    # Storage operations
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"File delete failed: {e}")
    # Cleanup folders safely
    if doc_type == "config" or doc_type == "contract":
        if not folder_name:
            project_root = f"{UPLOAD_DIR}/{user_id}/{project_id}/"
        else:
            project_root = f"{UPLOAD_DIR}/{user_id}/{project_id}"
    elif doc_type == "risk-assessment":
        project_root = f"{RISK_SUMMARY_DIR}/{user_id}/{project_id}"
    start_folder = os.path.dirname(file_path)

    cleanup_empty_dirs(start_folder, project_root)
