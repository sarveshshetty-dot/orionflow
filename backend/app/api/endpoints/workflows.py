from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db_session
from app.models.workflows import Workflow
from app.models.workflow_runs import WorkflowRun
from app.schemas.workflows import WorkflowCreate, WorkflowResponse, WorkflowRunWithLogs
from app.workflows.engine import WorkflowEngine

router = APIRouter()

@router.post("/", response_model=WorkflowResponse)
async def create_workflow(workflow_in: WorkflowCreate, db: AsyncSession = Depends(get_db_session)):
    # Assuming user_id=1 for now since auth isn't fully implemented
    workflow = Workflow(
        name=workflow_in.name,
        description=workflow_in.description,
        steps=[step.model_dump() for step in workflow_in.steps],
        user_id=1
    )
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    return workflow

@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Workflow).offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/{workflow_id}/run", response_model=WorkflowRunWithLogs)
async def run_workflow(workflow_id: int, db: AsyncSession = Depends(get_db_session)):
    engine = WorkflowEngine(db=db)
    try:
        run = await engine.start_workflow(workflow_id)
        return run
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{workflow_id}/runs", response_model=List[WorkflowRunWithLogs])
async def list_workflow_runs(workflow_id: int, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(
        select(WorkflowRun).where(WorkflowRun.workflow_id == workflow_id).order_by(WorkflowRun.id.desc())
    )
    return result.scalars().all()

@router.get("/runs", response_model=List[WorkflowRunWithLogs])
async def list_all_runs(limit: int = 50, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(
        select(WorkflowRun).order_by(WorkflowRun.id.desc()).limit(limit)
    )
    return result.scalars().all()
