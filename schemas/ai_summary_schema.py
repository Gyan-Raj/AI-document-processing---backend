from pydantic import BaseModel
from typing import List

class SectionAssessment(BaseModel):
    section: str
    subject: str
    summary: str

class SummaryResponse(BaseModel):
    overall_risk: str   # LOW | MEDIUM | HIGH | CRITICAL
    risk_score: int     # 0-100
    sections: List[SectionAssessment]
    remarks: str