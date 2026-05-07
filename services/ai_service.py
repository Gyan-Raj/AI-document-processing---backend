import os
import json
from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from db.connection import AsyncSessionLocal
from dao.project_dao import get_project_details_dao
from dao.contract_dao import get_contract_dao
from dao.config_dao import get_config_path_dao
from services.risk_summary_service import add_risk_summary_path
from services.embedding_and_chunks_service import embed_and_store_chunks
from ai_models.generate_summary import generate_summary
from utils.config_reader import read_config_file
from config.constants import RISK_SUMMARY_DIR
from utils.embedding_and_chunk import extract_text
from config.env_constants import MODEL_TO_BE_USED


async def run_assessment_and_generate_summary(user_id, project_id, background_tasks):
    # Step 1 — fetch all data
    async with AsyncSessionLocal() as session:
        project = await get_project_details_dao(session, project_id, user_id)
        contracts = await get_contract_dao(session, project_id)
        configs = await get_config_path_dao(session, project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not contracts:
        raise HTTPException(
            status_code=404, detail="No contracts found for this project"
        )

    # Guard 1 — still in flight
    if any(c["embedding_status"] == "processing" for c in contracts):
        print("embedding is in progress")
        return JSONResponse(
            status_code=202,
            content={
                "status_code": 202,
                "detail": "Documents are still being processed. Please try again in a moment.",
            },
        )

    # Guard 2 — some failed, retry them
    if any(c["embedding_status"] in ("failed", "pending") for c in contracts):
        for contract in contracts:
            if contract["embedding_status"] in ("failed", "pending"):
                background_tasks.add_task(
                    embed_and_store_chunks,
                    user_id,
                    project_id,
                    contract["id"],
                    contract["contract_path"],
                )
        return JSONResponse(
            status_code=202,
            content={
                "status_code": 202,
                "detail": "Some documents failed/not started and are being retried/started. Please try again in a moment.",
            },
        )

    # All completed — fall through to assessment
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

    # ADD this import at the top
    from services.embedding_and_chunks_service import retrieve_context_for_config

    # Step 4 — retrieve relevant chunks per folder using RAG
    all_folder_assessments = []

    for folder_name, folder_contracts in folder_contracts_map.items():
        config_path = folder_config_map.get(folder_name) or global_config_path
        config_rows = read_config_file(config_path)

        # Get the contract_ids for this folder
        folder_contract_ids = [c["id"] for c in folder_contracts]

        # RAG: retrieve relevant chunks instead of full text
        # We pass project_id — the DAO already filters by project
        retrieved_context = await retrieve_context_for_config(
            project_id=project_id,
            config_rows=config_rows,
        )

        if not retrieved_context.strip():
            # Fallback: if RAG returns nothing, use full text (old behavior)
            print(
                f"Warning: RAG returned no chunks for folder {folder_name}, falling back to full text"
            )
            folder_text_parts = []
            for contract in folder_contracts:
                path = contract["contract_path"]
                if path and os.path.exists(path):
                    text = extract_text(path)
                    if text.strip():
                        folder_text_parts.append(text)
            retrieved_context = "\n\n".join(folder_text_parts)[:12000]

        folder_label = folder_name if folder_name else "Root"
        all_folder_assessments.append(
            {
                "folder": folder_label,
                "text": retrieved_context,  # ← chunks, not full text
                "config_rows": config_rows,
                "config_used": os.path.basename(config_path) if config_path else None,
            }
        )

    # Step 5 — run AI assessment (unchanged)
    full_text = "\n\n".join(
        f"=== {fa['folder']} ===\n{fa['text']}" for fa in all_folder_assessments
    )
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
