from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.tasks import calculate_pi
from celery.result import AsyncResult

app = FastAPI(
    title="Pi Calculator Wiki",
    description="Calculate π using real astronomical data from Wikipedia",
    version="1.0.0")

class TaskResponse(BaseModel):
    task_id: str
    status: str

class ProgressResponse(BaseModel):
    state: str
    progress: float
    result: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    current_object: Optional[str] = None

class ObjectData(BaseModel):
    name: str
    radius_km: Optional[float] = None
    circumference_km: Optional[float] = None
    calculated_pi: Optional[float] = None
    error_percent: Optional[float] = None
    error: Optional[str] = None

@app.get("/", tags=["Root"])
def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to Pi Space Calculator! Today I will be fetching radius and circumference of the planets from Wikipedia and using it to calculate Pi :)",
        "docs": "/docs",
        "endpoints": {
            "calculate": "/calculate_pi?n=3",
            "progress": "/check_progress?task_id=YOUR_TASK_ID"
        }
    }

@app.get("/calculate_pi", response_model=TaskResponse, tags=["Calculate"])
def start_calculation(
    n: int = Query(
        default=3,
        ge=1,
        le=3,
        description="Number of objects to use (1-3)"
    )
):
    task = calculate_pi.delay(n)
    
    return TaskResponse(
        task_id=task.id,
        status=task.state
    )


@app.get("/check_progress", response_model=ProgressResponse, tags=["Progress"])
def check_task_progress(
    task_id: str = Query(..., description="Task ID from /calculate_pi")
):
    task = AsyncResult(task_id, app=calculate_pi.app)
    
    if task.state == 'PENDING':
        response = ProgressResponse(
            state='PENDING',
            progress=0.0,
            result=None,
            status='Task is waiting to start...'
        )
    
    elif task.state == 'PROGRESS':
        response = ProgressResponse(
            state='PROGRESS',
            progress=task.info.get('progress', 0),
            result=None,
            status=task.info.get('status', 'Processing...'),
            current_object=task.info.get('current_object')
        )
    elif task.state == 'SUCCESS':
        response = ProgressResponse(
            state='SUCCESS',
            progress=1.0,
            result=task.result
        )
    elif task.state == 'FAILURE':
        raise HTTPException(
            status_code=500,
            detail=f"Task failed: {str(task.info)}"
        )
    
    else:
        response = ProgressResponse(
            state=task.state,
            progress=0.0,
            result=None
        )
    
    return response

        