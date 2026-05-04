from pydantic import BaseModel

class RunAssessmentAndGenerateSummaryRequest(BaseModel):
    project_id:int