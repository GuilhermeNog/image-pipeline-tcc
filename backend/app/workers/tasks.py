import json
import time
import uuid
from datetime import datetime, timezone

import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.engine.executor import PipelineExecutor
from app.models.image import Image
from app.models.job import Job, JobStatus
from app.models.job_step import JobStep, StepStatus
from app.services.storage_service import load_image, save_step_result
from app.workers.celery_app import celery_app

import app.engine.operations  # noqa: F401

sync_engine = create_engine(settings.DATABASE_URL_SYNC)
SyncSession = sessionmaker(sync_engine, class_=Session)

redis_client = redis.from_url(settings.REDIS_URL)


def publish_progress(job_id: str, step: int, total: int, operation: str, result_path: str):
    message = json.dumps(
        {
            "job_id": job_id,
            "step": step,
            "total": total,
            "operation": operation,
            "result_path": result_path,
            "status": "processing",
        }
    )
    redis_client.publish(f"job:{job_id}:progress", message)


@celery_app.task(name="execute_pipeline", bind=True)
def execute_pipeline(self, job_id: str):
    with SyncSession() as db:
        job = db.query(Job).filter(Job.id == uuid.UUID(job_id)).first()
        if not job:
            return {"error": "Job not found"}

        job.status = JobStatus.PROCESSING
        job.started_at = datetime.now(timezone.utc)
        db.commit()

        try:
            image_record = db.query(Image).filter_by(id=job.image_id).first()
            if not image_record:
                raise FileNotFoundError("Image record not found")

            image = load_image(image_record.file_path)
            steps = db.query(JobStep).filter(JobStep.job_id == job.id).order_by(JobStep.step_number).all()
            executor = PipelineExecutor()

            operations = [
                {"type": step.operation_type, "params": step.operation_params or {}} for step in steps
            ]

            step_start_times = {}

            def on_step(step_num, total, operation, result_image):
                step_record = steps[step_num - 1]
                start_time = step_start_times.get(step_num, time.time())

                result_path = save_step_result(job.id, step_num, operation, result_image)

                step_record.result_image_path = result_path
                step_record.status = StepStatus.COMPLETED
                step_record.processing_time_ms = int((time.time() - start_time) * 1000)
                job.current_step = step_num
                db.commit()

                publish_progress(job_id, step_num, total, operation, result_path)

            # Record start times
            for i in range(len(operations)):
                step_start_times[i + 1] = time.time()

            executor.execute(image, operations, on_step=on_step)

            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)
            db.commit()

            redis_client.publish(
                f"job:{job_id}:progress",
                json.dumps(
                    {
                        "job_id": job_id,
                        "status": "completed",
                    }
                ),
            )

            return {"status": "completed", "job_id": job_id}

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            db.commit()

            redis_client.publish(
                f"job:{job_id}:progress",
                json.dumps(
                    {
                        "job_id": job_id,
                        "status": "failed",
                        "error": str(e),
                    }
                ),
            )

            return {"status": "failed", "error": str(e)}
