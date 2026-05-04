from db.connection import AsyncSessionLocal
from dao.project_dao import (
    create_project_dao,
    delete_project_dao,
    get_project_details_dao,
    get_all_projects_dao,
)
from dao.risk_summary_path_dao import get_risk_summary_path_dao
from services.contract_service import get_contract_path
from services.config_service import get_config_path
from services.risk_summary_service import get_risk_summary_path
import os
import shutil
import json
from utils.generate_pdf_from_json import generate_pdf_from_json
from utils.folder_structure import build_folder_structure
from fastapi.responses import FileResponse
from fastapi import HTTPException
from config.constants import UPLOAD_DIR


async def create_project(projectName, user_id):
    if not projectName:
        raise HTTPException(status_code=400, detail="Project name is missing")
    async with AsyncSessionLocal() as session:
        project = await create_project_dao(session, projectName, user_id)
        await session.commit()
        return project


async def delete_project(project_id, user_id):
    if not project_id:
        raise HTTPException(status_code=400, detail="Project id is missing")
    async with AsyncSessionLocal() as session:
        await delete_project_dao(session, project_id, user_id)
        await session.commit()

    RISK_SUMMARY_DIR = "user_files/risk_summaries"
    upload_folder_path = f"{UPLOAD_DIR}/{user_id}/{project_id}"
    risk_summary_folder_path = f"{RISK_SUMMARY_DIR}/{user_id}/{project_id}"
    for path in [upload_folder_path, risk_summary_folder_path]:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
            except Exception as e:
                print(f"Failed to delete project files from storage: {e}")


async def get_project_details(project_id, user_id):
    async with AsyncSessionLocal() as session:
        project = await get_project_details_dao(session, project_id, user_id)

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        contract_paths = await get_contract_path(session, project_id)
        config_paths = await get_config_path(session, project_id)
        risk_summary_paths = await get_risk_summary_path(session, project_id)

        folder_structure = build_folder_structure(contract_paths, config_paths)

    # outside session

    risk_data = None

    if risk_summary_paths:
        path = risk_summary_paths[0]["risk_summary_path"]

        if path and os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    risk_data = json.load(f)
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="Summary file is corrupted")

    return {
        "project": project,
        "risk_summary": risk_data,
        "folder_structure": folder_structure,
    }


async def get_all_projects(user_id, query):
    async with AsyncSessionLocal() as session:
        projects = await get_all_projects_dao(session, user_id, query)
        return projects


async def download_risk_summary(user_id, project_id, file_type):
    async with AsyncSessionLocal() as session:
        risk_summary_path = await get_risk_summary_path_dao(session, project_id)

    if not risk_summary_path:
        raise HTTPException(status_code=404, detail="No risk summary found")

    latest = risk_summary_path[0]
    json_path = latest["risk_summary_path"]

    if not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail="File missing")

    if file_type == "docx":
        file_path = json_path.replace(".json", ".docx")
        if not os.path.exists(file_path):
            generate_docx_from_json(json_path, file_path)
        media_type = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    else:
        file_path = json_path.replace(".json", ".pdf")
        if not os.path.exists(file_path):
            generate_pdf_from_json(json_path, file_path)
        media_type = "application/pdf"

    return FileResponse(
        path=file_path,
        filename=f"risk_summary.{file_type}",
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename=risk_summary.{file_type}"
        },
    )
