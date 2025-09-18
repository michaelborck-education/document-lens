"""
Batch processing service for large-scale document analysis
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import HTTPException

from app.models.schemas import (
    BatchJobCreate,
    BatchJobResponse,
    BatchJobStatus,
    BatchItemCreate,
    BatchItemStatus,
    BatchExportRequest,
    BatchExportResponse
)


class BatchService:
    """Service for managing batch document analysis jobs"""

    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.items: Dict[str, List[Dict[str, Any]]] = {}
        self.exports_dir = Path("exports")
        self.exports_dir.mkdir(exist_ok=True)

    async def create_job(self, job_data: BatchJobCreate) -> BatchJobResponse:
        """Create a new batch processing job"""
        job_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        job = {
            "id": job_id,
            "name": job_data.name,
            "description": job_data.description,
            "created_at": now,
            "updated_at": now,
            "analysis_type": job_data.analysis_type,
            "analysis_options": job_data.analysis_options,
            "priority": job_data.priority,
            "max_retries": job_data.max_retries,
            "status": {
                "total_items": 0,
                "completed_items": 0,
                "failed_items": 0,
                "progress_percentage": 0.0,
                "current_status": "created",
                "estimated_completion": None
            }
        }

        self.jobs[job_id] = job
        self.items[job_id] = []

        return BatchJobResponse(**job, result_count=0)

    async def get_job(self, job_id: str) -> BatchJobResponse:
        """Get job information by ID"""
        if job_id not in self.jobs:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        job = self.jobs[job_id]
        result_count = len([item for item in self.items.get(job_id, []) if item.get("status") == "completed"])

        return BatchJobResponse(**job, result_count=result_count)

    async def list_jobs(self, limit: int = 100, offset: int = 0) -> List[BatchJobResponse]:
        """List all batch jobs with pagination"""
        jobs_list = list(self.jobs.values())
        jobs_slice = jobs_list[offset:offset + limit]

        result = []
        for job in jobs_slice:
            job_id = job["id"]
            result_count = len([item for item in self.items.get(job_id, []) if item.get("status") == "completed"])
            result.append(BatchJobResponse(**job, result_count=result_count))

        return result

    async def add_items(self, job_id: str, items_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add items to a batch job"""
        if job_id not in self.jobs:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        job = self.jobs[job_id]
        if job["status"]["current_status"] not in ["created", "paused"]:
            raise HTTPException(
                status_code=400,
                detail="Cannot add items to a job that is running, completed, failed, or cancelled"
            )

        now = datetime.utcnow().isoformat()
        new_items = []

        for item_data in items_data:
            item_id = str(uuid.uuid4())
            item = {
                "id": item_id,
                "job_id": job_id,
                "status": "pending",
                "input_data": item_data,
                "result_data": None,
                "error_message": None,
                "retry_count": 0,
                "created_at": now,
                "processed_at": None,
                "processing_time": None
            }
            new_items.append(item)

        self.items[job_id].extend(new_items)

        # Update job status
        total_items = len(self.items[job_id])
        self.jobs[job_id]["status"]["total_items"] = total_items
        self.jobs[job_id]["updated_at"] = now

        return {
            "message": f"Added {len(new_items)} items to job {job_id}",
            "items_added": len(new_items),
            "total_items": total_items
        }

    async def start_job(self, job_id: str) -> Dict[str, Any]:
        """Start processing a batch job"""
        if job_id not in self.jobs:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        job = self.jobs[job_id]
        if job["status"]["current_status"] not in ["created", "paused"]:
            raise HTTPException(
                status_code=400,
                detail="Can only start jobs that are in 'created' or 'paused' status"
            )

        if not self.items.get(job_id):
            raise HTTPException(
                status_code=400,
                detail="Cannot start job with no items"
            )

        # Update status to running
        job["status"]["current_status"] = "running"
        job["updated_at"] = datetime.utcnow().isoformat()

        # Start background processing
        asyncio.create_task(self._process_job_items(job_id))

        return {"message": f"Job {job_id} started", "status": "running"}

    async def pause_job(self, job_id: str) -> Dict[str, Any]:
        """Pause a running batch job"""
        if job_id not in self.jobs:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        job = self.jobs[job_id]
        if job["status"]["current_status"] != "running":
            raise HTTPException(
                status_code=400,
                detail="Can only pause jobs that are running"
            )

        job["status"]["current_status"] = "paused"
        job["updated_at"] = datetime.utcnow().isoformat()

        return {"message": f"Job {job_id} paused", "status": "paused"}

    async def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """Cancel a batch job"""
        if job_id not in self.jobs:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        job = self.jobs[job_id]
        job["status"]["current_status"] = "cancelled"
        job["updated_at"] = datetime.utcnow().isoformat()

        return {"message": f"Job {job_id} cancelled", "status": "cancelled"}

    async def get_job_items(self, job_id: str, status_filter: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[BatchItemStatus]:
        """Get items for a specific job with optional filtering"""
        if job_id not in self.jobs:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        items = self.items.get(job_id, [])

        if status_filter:
            items = [item for item in items if item["status"] == status_filter]

        items_slice = items[offset:offset + limit]
        return [BatchItemStatus(**item) for item in items_slice]

    async def export_results(self, job_id: str, export_request: BatchExportRequest) -> BatchExportResponse:
        """Export batch job results to various formats"""
        if job_id not in self.jobs:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        items = self.items.get(job_id, [])

        # Filter items by status if specified
        if export_request.filter_status:
            items = [item for item in items if item["status"] in export_request.filter_status]

        if not items:
            raise HTTPException(status_code=404, detail="No items found matching the filter criteria")

        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"batch_export_{job_id}_{timestamp}.{export_request.export_format}"
        filepath = self.exports_dir / filename

        # Export data based on format
        if export_request.export_format == "jsonl":
            await self._export_jsonl(items, filepath, export_request.include_metadata)
        elif export_request.export_format == "csv":
            await self._export_csv(items, filepath, export_request.include_metadata)
        elif export_request.export_format == "parquet":
            await self._export_parquet(items, filepath, export_request.include_metadata)

        # Calculate file size
        file_size = filepath.stat().st_size

        # Create download URL (in production, this would be a signed URL or similar)
        download_url = f"/batch/download/{filename}"

        # Set expiration (7 days from now)
        expires_at = (datetime.utcnow() + timedelta(days=7)).isoformat()

        return BatchExportResponse(
            download_url=download_url,
            export_format=export_request.export_format,
            file_size_bytes=file_size,
            item_count=len(items),
            created_at=datetime.utcnow().isoformat(),
            expires_at=expires_at
        )

    async def _process_job_items(self, job_id: str):
        """Background task to process job items"""
        job = self.jobs[job_id]
        items = self.items[job_id]

        for item in items:
            # Check if job is paused or cancelled
            if job["status"]["current_status"] in ["paused", "cancelled"]:
                break

            if item["status"] != "pending":
                continue

            try:
                # Update item status to processing
                item["status"] = "processing"
                item["processed_at"] = datetime.utcnow().isoformat()

                # Simulate processing (replace with actual document analysis)
                await self._process_single_item(job_id, item)

                # Update item status to completed
                item["status"] = "completed"
                job["status"]["completed_items"] += 1

            except Exception as e:
                item["status"] = "failed"
                item["error_message"] = str(e)
                job["status"]["failed_items"] += 1

                # Retry logic
                if item["retry_count"] < job["max_retries"]:
                    item["retry_count"] += 1
                    item["status"] = "pending"  # Retry
                    job["status"]["failed_items"] -= 1

            # Update progress
            total = job["status"]["total_items"]
            completed = job["status"]["completed_items"]
            failed = job["status"]["failed_items"]
            progress = ((completed + failed) / total * 100) if total > 0 else 0
            job["status"]["progress_percentage"] = round(progress, 2)

            # Small delay to prevent overwhelming
            await asyncio.sleep(0.1)

        # Mark job as completed if all items are processed
        total = job["status"]["total_items"]
        processed = job["status"]["completed_items"] + job["status"]["failed_items"]
        if processed >= total:
            job["status"]["current_status"] = "completed"
            job["updated_at"] = datetime.utcnow().isoformat()

    async def _process_single_item(self, job_id: str, item: Dict[str, Any]):
        """Process a single item (mock implementation)"""
        start_time = datetime.utcnow()

        # Mock processing - replace with actual document analysis
        input_data = item["input_data"]

        # Simulate analysis result
        result = {
            "analysis_type": self.jobs[job_id]["analysis_type"],
            "word_count": len(input_data.get("text", "").split()) if input_data.get("text") else 0,
            "readability_score": 75.5,  # Mock score
            "processed_at": datetime.utcnow().isoformat()
        }

        item["result_data"] = result

        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        item["processing_time"] = processing_time

    async def _export_jsonl(self, items: List[Dict[str, Any]], filepath: Path, include_metadata: bool):
        """Export items to JSONL format"""
        with open(filepath, 'w') as f:
            for item in items:
                if include_metadata:
                    f.write(json.dumps(item) + '\n')
                else:
                    # Only export result data
                    if item.get("result_data"):
                        f.write(json.dumps(item["result_data"]) + '\n')

    async def _export_csv(self, items: List[Dict[str, Any]], filepath: Path, include_metadata: bool):
        """Export items to CSV format"""
        data = []
        for item in items:
            if include_metadata:
                # Flatten the nested structure
                row = {
                    "item_id": item["id"],
                    "status": item["status"],
                    "created_at": item["created_at"],
                    "processed_at": item["processed_at"],
                    "processing_time": item["processing_time"],
                    "retry_count": item["retry_count"]
                }
                # Add result data fields
                if item.get("result_data"):
                    for key, value in item["result_data"].items():
                        row[f"result_{key}"] = value
                data.append(row)
            else:
                # Only result data
                if item.get("result_data"):
                    data.append(item["result_data"])

        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)

    async def _export_parquet(self, items: List[Dict[str, Any]], filepath: Path, include_metadata: bool):
        """Export items to Parquet format"""
        data = []
        for item in items:
            if include_metadata:
                # Flatten the nested structure
                row = {
                    "item_id": item["id"],
                    "status": item["status"],
                    "created_at": item["created_at"],
                    "processed_at": item["processed_at"],
                    "processing_time": item["processing_time"],
                    "retry_count": item["retry_count"]
                }
                # Add result data fields
                if item.get("result_data"):
                    for key, value in item["result_data"].items():
                        row[f"result_{key}"] = value
                data.append(row)
            else:
                # Only result data
                if item.get("result_data"):
                    data.append(item["result_data"])

        df = pd.DataFrame(data)
        df.to_parquet(filepath, index=False)


# Global service instance
batch_service = BatchService()