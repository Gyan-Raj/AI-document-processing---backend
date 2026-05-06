from fastapi import APIRouter, Request, UploadFile, File, Form, BackgroundTasks
from services.document_service import upload_document, delete_document
import json
from schemas.document_schema import DeleteDocumentRequest

document_router = APIRouter()


@document_router.post("/document")
async def upload_document_route(
    request: Request,
    background_tasks: BackgroundTasks,
    project_id: int = Form(...),
    structure: str = Form(...),  # ✅ receive JSON
):
    parsed_structure = json.loads(structure)

    # access all uploaded files
    form = await request.form()

    for folder in parsed_structure:
        folder_name = folder["folderName"]

        for file_meta in folder["files"]:
            file_name = file_meta["fileName"]
            file_type = file_meta["type"]

            file: UploadFile = form.get(f"{folder_name}-{file_name}")

            if not file:
                raise Exception(f"File missing for {folder_name}")

            await upload_document(
                file,
                project_id,
                request.state.user_id,
                folder_name,
                file_type,
                file_name,
                background_tasks,
            )

    return {"message": "Upload successful"}


@document_router.delete("/document")
async def delete_document_route(request: Request, data: DeleteDocumentRequest):
    doc_id = data.doc_id
    doc_type = data.doc_type
    project_id = data.project_id
    await delete_document(request.state.user_id, project_id, doc_id, doc_type)
    return {"message": "Document deleted successfully"}
