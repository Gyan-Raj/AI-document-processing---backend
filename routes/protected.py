from fastapi import APIRouter, Depends
from middleware.auth_middleware import auth_required
from routes.user import user_router
from routes.projects import project_router
from routes.document import document_router
from routes.ai import ai_router

protected_router = APIRouter(dependencies=[Depends(auth_required)])

protected_router.include_router(user_router)
protected_router.include_router(project_router)
protected_router.include_router(document_router)
protected_router.include_router(ai_router)
# protected_router.include_router(products_router, prefix="/products")
