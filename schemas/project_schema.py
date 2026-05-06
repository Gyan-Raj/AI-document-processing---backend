from pydantic import BaseModel


class CreateProjectRequest(BaseModel):
    project_name: str
