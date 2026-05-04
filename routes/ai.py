from fastapi import APIRouter, Request
from schemas.ai_schema import RunAssessmentAndGenerateSummaryRequest
from services.ai_service import run_assessment_and_generate_summary
ai_router = APIRouter()
@ai_router.post("/run-assessment-and-generate-summary")
async def run_assessment_and_generate_summary_route(request: Request, data: RunAssessmentAndGenerateSummaryRequest):
    summary = await run_assessment_and_generate_summary(request.state.user_id, data.project_id)
    return {
        "message": "Assessment run and summary generated successfully",
        "data": summary
    }
