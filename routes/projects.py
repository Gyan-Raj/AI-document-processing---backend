from fastapi import APIRouter, Request, Query
from services.project_service import (
    create_project,
    delete_project,
    get_project_details,
    get_all_projects,
    download_risk_summary,
)
from schemas.project_schema import CreateProjectRequest

project_router = APIRouter()


@project_router.post("/create-project")
async def create_project_route(request: Request, data: CreateProjectRequest):
    print(data, "data")
    projectName = data.projectName
    project = await create_project(projectName, request.state.user_id)
    print(project, "project")
    return {"message": "Project created successfully", "project": project}


@project_router.get("/project/{id}")
async def get_project_details_route(request: Request, id: int):
    project = await get_project_details(id, request.state.user_id)
    return {"message": "Project fetched successfully", "project": project}


@project_router.delete("/project/{id}")
async def delete_project_route(request: Request, id: int):
    await delete_project(id, request.state.user_id)
    return {
        "message": "Project deleted successfully",
    }


@project_router.get("/all-projects")
async def get_all_projects_route(request: Request, query: str = ""):
    projects = await get_all_projects(request.state.user_id, query)
    return {"message": "Projects fetched successfully", "projects": projects}


@project_router.get("/download-risk-summary/{id}")
async def download_risk_summary_route(
    request: Request, id: int, type: str = Query("pdf")
):
    return await download_risk_summary(request.state.user_id, id, type)
