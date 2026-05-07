from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from config.env_constants import FRONTEND_ORIGINS
from routes.auth import auth_router

# from routes.user import router as user_router
from routes.protected import protected_router
from db.connection import check_db_connection

# from middleware.auth_middleware import auth_middleware
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app):
    await check_db_connection()
    yield


app = FastAPI(lifespan=lifespan)  # replaces deprecated @app.on_event("startup")

print(FRONTEND_ORIGINS, "FRONTEND_ORIGINS")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in FRONTEND_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "API is working"}


app.include_router(auth_router, prefix="/auth")
# app.include_router(user_router, dependencies=[Depends(auth_middleware)])  # ✅ protected
app.include_router(protected_router)
