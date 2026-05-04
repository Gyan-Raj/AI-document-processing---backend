from pydantic import BaseModel

class CreateProjectRequest(BaseModel):
    projectName: str
