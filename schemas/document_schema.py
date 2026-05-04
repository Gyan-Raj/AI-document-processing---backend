from pydantic import BaseModel

class DeleteDocumentRequest(BaseModel):
    doc_id: int
    doc_type: str
    project_id: int