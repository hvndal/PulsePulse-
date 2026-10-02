import asyncio
import time
from typing import Dict, Optional, List
from backend.models import QueueJob, JobStatus

class QueueManager:
    """
    Persistent, asynchronous queue manager for long-form speech generation jobs.
    Supports pause, resume, and failure recovery.
    """

    def __init__(self):
        self.jobs: Dict[str, QueueJob] = {}

    def create_job(self, project_id: str, chapter_id: Optional[str] = None, paragraph_id: Optional[str] = None) -> QueueJob:
        job = QueueJob(
            project_id=project_id,
            chapter_id=chapter_id,
            paragraph_id=paragraph_id,
            status=JobStatus.QUEUED,
            progress_percentage=0.0,
            current_item="Job Enqueued"
        )
        self.jobs[job.id] = job
        return job

    def get_job(self, job_id: str) -> Optional[QueueJob]:
        return self.jobs.get(job_id)

    def list_jobs(self, project_id: Optional[str] = None) -> List[QueueJob]:
        if project_id:
            return [j for j in self.jobs.values() if j.project_id == project_id]
        return list(self.jobs.values())

    def update_job_progress(self, job_id: str, progress: float, current_item: str, status: Optional[JobStatus] = None) -> Optional[QueueJob]:
        job = self.jobs.get(job_id)
        if not job:
            return None

        job.progress_percentage = max(0.0, min(100.0, progress))
        job.current_item = current_item
        if status:
            job.status = status
        job.updated_at = time.time()
        return job

    def pause_job(self, job_id: str) -> Optional[QueueJob]:
        job = self.jobs.get(job_id)
        if job and job.status == JobStatus.PROCESSING:
            job.status = JobStatus.PAUSED
            job.updated_at = time.time()
        return job

    def resume_job(self, job_id: str) -> Optional[QueueJob]:
        job = self.jobs.get(job_id)
        if job and job.status == JobStatus.PAUSED:
            job.status = JobStatus.PROCESSING
            job.updated_at = time.time()
        return job
