"""
Background task processor service.
"""
import asyncio
import logging
import datetime
from datetime import datetime as date
from typing import Optional

from src.core.config import get_settings
from src.database import db

settings = get_settings()
logger = logging.getLogger(__name__)

class TaskProcessor:
    """Service that processes queued tasks in the background."""
    
    def __init__(self):
        """Initialize the task processor."""
        self.is_running = False
        self.worker_task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start the task processor."""
        if self.is_running:
            logger.warning("Task processor is already running")
            return
        
        logger.info("Starting task processor...")
        self.is_running = True
        self.worker_task = asyncio.create_task(self._process_queue())
        logger.info("Task processor started")
    
    async def stop(self) -> None:
        """Stop the task processor."""
        if not self.is_running:
            logger.warning("Task processor is not running")
            return
        
        logger.info("Stopping task processor...")
        self.is_running = False
        
        if self.worker_task:
            try:
                await asyncio.wait_for(self.worker_task, timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("Task processor did not stop gracefully, cancelling...")
                self.worker_task.cancel()
                try:
                    await self.worker_task
                except asyncio.CancelledError:
                    logger.info("Task processor cancelled")
        
        logger.info("Task processor stopped")
    
    async def _process_queue(self) -> None:
        """Process tasks from the queue continuously."""
        tasks_collection = db.get_collection("uploads")
        
        while self.is_running:
            try:
                # Find the oldest queued task with highest priority
                task = await tasks_collection.find_one_and_update(
                    {"status": settings.STATUS_QUEUED},
                    {"$set": {"status": settings.STATUS_PROCESSING, "updated_at": date.now(datetime.timezone.utc)}},
                    sort=[("priority", -1), ("created_at", 1)],
                    return_document=False
                )
                
                if task:
                    task_id = task["_id"]
                    logger.info(f"Processing task: {task_id}")
                    
                    try:
                        # Simulate task processing time
                        # In a real application, you would implement actual task execution logic here
                        await asyncio.sleep(settings.PROCESSING_TIME)
                        
                        # This is where you would implement the actual task processing logic
                        result = {"message": "Task completed successfully"}
                        
                        # Update task as completed
                        now = date.now(datetime.timezone.utc)
                        await tasks_collection.update_one(
                            {"_id": task_id},
                            {
                                "$set": {
                                    "status": settings.STATUS_COMPLETED,
                                    "updated_at": now,
                                    "completed_at": now,
                                    "result": result
                                }
                            }
                        )
                        logger.info(f"Task completed: {task_id}")
                    
                    except Exception as e:
                        # Update task as failed
                        await tasks_collection.update_one(
                            {"_id": task_id},
                            {
                                "$set": {
                                    "status": settings.STATUS_FAILED,
                                    "updated_at": date.now(datetime.timezone.utc),
                                    "error": str(e)
                                }
                            }
                        )
                        logger.error(f"Task failed: {task_id} - {str(e)}")
                
                else:
                    # No tasks to process, wait before checking again
                    await asyncio.sleep(settings.WORKER_SLEEP_TIME)
            
            except Exception as e:
                logger.error(f"Error in task processor: {str(e)}")
                # Wait before retrying after an error
                await asyncio.sleep(settings.ERROR_SLEEP_TIME)

# Global task processor instance
task_processor = TaskProcessor()