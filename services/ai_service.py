import os
import json
import pdfplumber
import asyncio
from datetime import datetime
from fastapi import HTTPException

from db.connection import AsyncSessionLocal
from dao.project_dao import get_project_details_dao
from dao.contract_path_dao import get_contract_path_dao
from dao.config_path_dao import get_config_path_dao
from services.risk_summary_service import add_risk_summary_path
from ai_models.generate_summary import generate_summary
from utils.config_reader import read_config_file
from config.constants import RISK_SUMMARY_DIR
from utils.helper import extract_text
from config.constants import MODEL_TO_BE_USED


async def run_assessment_and_generate_summary(user_id, project_id):
    # Step 1 — fetch all data
    async with AsyncSessionLocal() as session:
        project = await get_project_details_dao(session, project_id, user_id)
        contracts = await get_contract_path_dao(session, project_id)
        configs = await get_config_path_dao(session, project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not contracts:
        raise HTTPException(
            status_code=404, detail="No contracts found for this project"
        )

    # Step 2 — organize configs by folder
    # global config has folder_name = ""
    global_config_path = None
    folder_config_map = {}  # { "Folder 1": "/path/to/config.xlsx" }

    for cfg in configs:
        folder = (cfg["folder_name"] or "").strip()
        if folder == "":
            global_config_path = cfg["config_path"]
        else:
            folder_config_map[folder] = cfg["config_path"]

    # Step 3 — group contracts by folder
    folder_contracts_map = {}  # { "Folder 1": [contract_row, ...] }
    for contract in contracts:
        folder = (contract["folder_name"] or "").strip()
        folder_contracts_map.setdefault(folder, []).append(contract)

    # Step 4 — build combined text per folder, each with its correct config
    all_folder_assessments = []

    for folder_name, folder_contracts in folder_contracts_map.items():
        # pick config: folder-level first, fallback to global, fallback to None
        config_path = folder_config_map.get(folder_name) or global_config_path
        config_rows = read_config_file(config_path)  # [] if no config

        # extract and combine text from all contracts in this folder
        folder_text_parts = []
        for contract in folder_contracts:
            path = contract["contract_path"]
            if not path or not os.path.exists(path):
                print(f"Warning: contract file missing: {path}")
                continue
            text = extract_text(path)
            if text.strip():
                folder_text_parts.append(
                    f"--- Contract: {contract['contract_name']} ---\n{text}"
                )

        if not folder_text_parts:
            continue

        combined_text = "\n\n".join(folder_text_parts)
        folder_label = folder_name if folder_name else "Root"

        all_folder_assessments.append(
            {
                "folder": folder_label,
                "text": combined_text,
                "config_rows": config_rows,
                "config_used": os.path.basename(config_path) if config_path else None,
            }
        )

    if not all_folder_assessments:
        raise HTTPException(
            status_code=422, detail="Could not extract text from any contract"
        )

    # Step 5 — run AI assessment
    # combine all folder texts into one project-level assessment
    full_text = "\n\n".join(
        f"=== {fa['folder']} ===\n{fa['text']}" for fa in all_folder_assessments
    )
    # use the config from the first folder that has one, else global
    # (for project-level summary we pass the most relevant config)
    primary_config = next(
        (fa["config_rows"] for fa in all_folder_assessments if fa["config_rows"]), []
    )

    summary = await generate_summary(full_text, primary_config, MODEL_TO_BE_USED)

    # Step 6 — attach metadata about which config was used per folder
    summary["meta"]["folder_config_mapping"] = [
        {
            "folder": fa["folder"],
            "config_used": fa["config_used"] or "none (generic assessment)",
        }
        for fa in all_folder_assessments
    ]

    # Step 7 — save to disk
    folder_path = f"{RISK_SUMMARY_DIR}/{user_id}/{project_id}"
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    os.makedirs(folder_path, exist_ok=True)
    file_path = f"{folder_path}/Risk_summary_{timestamp}.json"

    with open(file_path, "w") as f:
        json.dump(summary, f, indent=2)

    await add_risk_summary_path(user_id, project_id, file_path)
    return summary
