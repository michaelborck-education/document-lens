"""
Batch processing API endpoints for large-scale document analysis
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse

from app.models.schemas import (
    BatchJobCreate,
    BatchJobResponse,
    BatchItemCreate,
    BatchItemStatus,
    BatchExportRequest,
    BatchExportResponse
)
from app.services.batch_service import batch_service

router = APIRouter(prefix="/batch", tags=["batch"])


@router.post("/jobs", response_model=BatchJobResponse)
async def create_batch_job(job_data: BatchJobCreate):
    """
    Create a new batch processing job.

    This endpoint creates a new batch job for processing multiple documents.
    The job is created in 'created' status and can accept items before starting.
    """
    return await batch_service.create_job(job_data)


@router.get("/jobs", response_model=List[BatchJobResponse])
async def list_batch_jobs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    List all batch jobs with pagination.

    Returns a paginated list of all batch jobs with their current status.
    """
    return await batch_service.list_jobs(limit=limit, offset=offset)


@router.get("/jobs/{job_id}", response_model=BatchJobResponse)
async def get_batch_job(job_id: str):
    """
    Get detailed information about a specific batch job.

    Returns complete job information including current status,
    progress, and configuration.
    """
    return await batch_service.get_job(job_id)


@router.post("/jobs/{job_id}/items")
async def add_job_items(job_id: str, items_data: List[dict]):
    """
    Add items to a batch job.

    Items can only be added to jobs in 'created' or 'paused' status.
    Each item should contain the data needed for document analysis.

    Example item format:
    {
        "text": "Document text to analyze...",
        "filename": "document1.txt",
        "metadata": {"author": "John Doe", "date": "2024-01-01"}
    }
    """
    return await batch_service.add_items(job_id, items_data)


@router.post("/jobs/{job_id}/start")
async def start_batch_job(job_id: str):
    """
    Start processing a batch job.

    Changes job status from 'created' or 'paused' to 'running'.
    Processing will begin in the background.
    """
    return await batch_service.start_job(job_id)


@router.post("/jobs/{job_id}/pause")
async def pause_batch_job(job_id: str):
    """
    Pause a running batch job.

    Current items will finish processing, but no new items will be started.
    Job can be resumed using the start endpoint.
    """
    return await batch_service.pause_job(job_id)


@router.post("/jobs/{job_id}/cancel")
async def cancel_batch_job(job_id: str):
    """
    Cancel a batch job.

    Permanently stops the job. Cannot be resumed.
    Items currently processing will finish, but pending items will be skipped.
    """
    return await batch_service.cancel_job(job_id)


@router.get("/jobs/{job_id}/items", response_model=List[BatchItemStatus])
async def get_job_items(
    job_id: str,
    status: Optional[str] = Query(None, description="Filter by item status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Get items for a specific job with optional status filtering.

    Status filters: pending, processing, completed, failed, skipped
    """
    return await batch_service.get_job_items(
        job_id, status_filter=status, limit=limit, offset=offset
    )


@router.post("/jobs/{job_id}/export", response_model=BatchExportResponse)
async def export_job_results(job_id: str, export_request: BatchExportRequest):
    """
    Export batch job results to various formats.

    Supported formats:
    - jsonl: JSON Lines format (one JSON object per line)
    - csv: Comma-separated values
    - parquet: Apache Parquet format for efficient storage and analysis

    The export can include metadata (timestamps, retry counts, etc.) or just result data.
    Results can be filtered by item status.
    """
    export_request.job_id = job_id  # Ensure job_id matches URL parameter
    return await batch_service.export_results(job_id, export_request)


@router.get("/download/{filename}")
async def download_export(filename: str):
    """
    Download an exported batch results file.

    Files are available for 7 days after export creation.
    """
    from pathlib import Path

    filepath = Path("exports") / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Export file not found or expired")

    return FileResponse(
        path=str(filepath),
        filename=filename,
        media_type="application/octet-stream"
    )


# Health check specifically for batch processing
@router.get("/health")
async def batch_health():
    """
    Health check for batch processing system.

    Returns information about active jobs and system capacity.
    """
    jobs = await batch_service.list_jobs(limit=1000)

    active_jobs = len([job for job in jobs if job.status.current_status == "running"])
    total_jobs = len(jobs)

    return {
        "status": "healthy",
        "batch_system": "operational",
        "active_jobs": active_jobs,
        "total_jobs": total_jobs,
        "max_concurrent_jobs": 10,  # Configuration value
        "available_capacity": max(0, 10 - active_jobs)
    }