from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.endpoints import workflows, tasks, websockets, metrics, schedules

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for OrionFlow distributed workflow orchestrator",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For real-world use restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers (can be expanded later)

# Include routers
app.include_router(workflows.router, prefix=f"{settings.API_V1_STR}/workflows", tags=["workflows"])
app.include_router(tasks.router, prefix=f"{settings.API_V1_STR}/tasks", tags=["tasks"])
app.include_router(schedules.router, prefix=f"{settings.API_V1_STR}/schedules", tags=["schedules"])
app.include_router(metrics.router, prefix=f"{settings.API_V1_STR}/system", tags=["system"]) # system/metrics and system/workers
app.include_router(websockets.router, prefix="/ws", tags=["websockets"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
