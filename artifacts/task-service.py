import os
import uuid
import json
import logging
import time
import threading
from queue import Queue
from datetime import datetime, timedelta

from drumtrackkit.config import Config
from drumtrackkit.models.task import Task
from drumtrackkit import db
from drumtrackkit.services.analysis_service import AnalysisService
from drumtrackkit.services.youtube_service import YouTubeService

# Set up logging
logger = logging.getLogger(__name__)


class TaskService:
    """Service for managing background tasks and long-running operations"""

    def __init__(self):
        """Initialize the task service"""
        self.queue = Queue()
        self.workers = []
        self.running = True
        self.max_workers = Config.MAX_WORKER_THREADS
        self.youtube_service = YouTubeService()
        self.analysis_service = AnalysisService()

        # Start worker threads
        self._start_workers()

        # Clean up old tasks periodically
        self._schedule_cleanup()

    def _start_workers(self):
        """Start worker threads to process tasks"""
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                args=(i,),
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
            logger.info(f"Started worker thread {i}")

    def _worker_loop(self, worker_id):
        """Main loop for worker threads"""
        logger.info(f"Worker {worker_id} started")

        while self.running:
            try:
                # Get a task from the queue with a timeout
                try:
                    task_id = self.queue.get(timeout=5)
                except Queue.Empty:
                    continue

                logger.info(f"Worker {worker_id} processing task {task_id}")

                # Get task from database
                with db.session_scope() as session:
                    task = session.query(Task).filter_by(id=task_id).first()

                    if not task:
                        logger.warning(f"Task {task_id} not found in database")
                        self.queue.task_done()
                        continue

                    # Update task status
                    task.status = 'processing'
                    task.started_at = datetime.utcnow()
                    session.commit()

                # Process task based on type
                try:
                    if task.type == 'youtube_analysis':
                        self._process_youtube_analysis(task_id)
                    elif task.type == 'audio_analysis':
                        self._process_audio_analysis(task_id)
                    elif task.type == 'midi_analysis':
                        self._process_midi_analysis(task_id)
                    elif task.type == 'style_transfer':
                        self._process_style_transfer(task_id)
                    else:
                        logger.warning(f"Unknown task type: {task.type}")
                        self._mark_task_failed(task_id, f"Unknown task type: {task.type}")

                except Exception as e:
                    logger.error(f"Error processing task {task_id}: {str(e)}", exc_info=True)
                    self._mark_task_failed(task_id, str(e))

                # Mark task as done in queue
                self.queue.task_done()

            except Exception as e:
                logger.error(f"Error in worker {worker_id}: {str(e)}", exc_info=True)
                # Sleep to avoid tight loop on error
                time.sleep(1)

        logger.info(f"Worker {worker_id} stopped")

    def _process_youtube_analysis(self, task_id):
        """Process a YouTube analysis task"""
        with db.session_scope() as session:
            task = session.query(Task).filter_by(id=task_id).first()
            if not task:
                return

            parameters = task.parameters
            url = parameters.get('url')
            start_time = parameters.get('start_time', 0)
            duration = parameters.get('duration', 180)
            analysis_type = parameters.get('analysis_type', 'performance')
            analysis_id = parameters.get('analysis_id')

            # Update progress
            task.progress = 10
            session.commit()

            # Download audio from YouTube
            try:
                audio_path = self.youtube_service.download_audio(url, start_time, duration)
            except Exception as e:
                logger.error(f"Error downloading YouTube video: {str(e)}", exc_info=True)
                raise RuntimeError(f"Failed to download YouTube video: {str(e)}")

            # Update progress
            task.progress = 40
            session.commit()

            # Analyze audio
            try:
                analysis_result = self.analysis_service.analyze_audio(
                    audio_path,
                    analysis_type=analysis_type
                )
            except Exception as e:
                logger.error(f"Error analyzing audio: {str(e)}", exc_info=True)
                raise RuntimeError(f"Failed to analyze audio: {str(e)}")

            # Update progress
            task.progress = 90
            session.commit()

            # Update analysis record if analysis_id is provided
            if analysis_id:
                try:
                    analysis = session.query(Analysis).filter_by(id=analysis_id).first()
                    if analysis:
                        analysis.status = 'completed'
                        analysis.results = analysis_result
                        analysis.completed_at = datetime.utcnow()
                except Exception as e:
                    logger.error(f"Error updating analysis record: {str(e)}", exc_info=True)

            # Store result
            result_path = os.path.join(
                Config.RESULTS_DIR,
                f"youtube_analysis_{task_id}.json"
            )
            os.makedirs(os.path.dirname(result_path), exist_ok=True)

            with open(result_path, 'w') as f:
                json.dump(analysis_result, f)

            # Update task status
            task.status = 'completed'
            task.progress = 100
            task.completed_at = datetime.utcnow()
            task.result = {"result_path": result_path}
            session.commit()

            logger.info(f"YouTube analysis task {task_id} completed successfully")

    def _process_audio_analysis(self, task_id):
        """Process an audio analysis task"""
        # Implementation similar to _process_youtube_analysis but with direct audio file
        pass

    def _process_midi_analysis(self, task_id):
        """Process a MIDI analysis task"""
        # Implementation for MIDI analysis
        pass

    def _process_style_transfer(self, task_id):
        """Process a style transfer task"""
        # Implementation for style transfer
        pass

    def _mark_task_failed(self, task_id, error_message):
        """Mark a task as failed with an error message"""
        try:
            with db.session_scope() as session:
                task = session.query(Task).filter_by(id=task_id).first()
                if task:
                    task.status = 'failed'
                    task.error = {"message": error_message}
                    task.completed_at = datetime.utcnow()
                    session.commit()
        except Exception as e:
            logger.error(f"Error marking task {task_id} as failed: {str(e)}", exc_info=True)

    def _schedule_cleanup(self):
        """Schedule periodic cleanup of old tasks"""
        cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True
        )
        cleanup_thread.start()
        logger.info("Started task cleanup thread")

    def _cleanup_loop(self):
        """Periodically clean up old completed tasks"""
        while self.running:
            try:
                # Sleep for a day
                time.sleep(86400)  # 24 hours

                # Clean up tasks older than the retention period
                self._cleanup_old_tasks()

            except Exception as e:
                logger.error(f"Error in cleanup loop: {str(e)}", exc_info=True)
                # Sleep to avoid tight loop on error
                time.sleep(3600)  # 1 hour

    def _cleanup_old_tasks(self):
        """Clean up tasks older than the retention period"""
        try:
            # Calculate cutoff date (30 days by default)
            cutoff_date = datetime.utcnow() - timedelta(days=Config.TASK_RETENTION_DAYS)

            with db.session_scope() as session:
                # Find completed or failed tasks older than cutoff date
                old_tasks = session.query(Task).filter(
                    Task.status.in_(['completed', 'failed']),
                    Task.completed_at < cutoff_date
                ).all()

                for task in old_tasks:
                    # Delete result files if they exist
                    if task.result and 'result_path' in task.result:
                        try:
                            result_path = task.result['result_path']
                            if os.path.exists(result_path):
                                os.remove(result_path)
                        except Exception as e:
                            logger.warning(f"Error removing result file for task {task.id}: {str(e)}")

                    # Delete the task
                    session.delete(task)

                session.commit()
                logger.info(f"Cleaned up {len(old_tasks)} old tasks")

        except Exception as e:
            logger.error(f"Error cleaning up old tasks: {str(e)}", exc_info=True)

    def create_job(self, job_type, parameters, user_id):
        """
        Create a new background job

        Args:
            job_type (str): Type of job to create
            parameters (dict): Parameters for the job
            user_id (str): ID of the user creating the job

        Returns:
            str: Job ID
        """
        job_id = str(uuid.uuid4())

        # Create task record
        task = Task(
            id=job_id,
            type=job_type,
            parameters=parameters,
            user_id=user_id,
            status='queued',
            progress=0,
            created_at=datetime.utcnow()
        )

        # Save to database
        with db.session_scope() as session:
            session.add(task)
            session.commit()

        # Add to processing queue
        self.queue.put(job_id)

        logger.info(f"Created job {job_id} of type {job_type} for user {user_id}")

        return job_id

    def get_job_status(self, job_id, user_id=None):
        """
        Get the status of a job

        Args:
            job_id (str): ID of the job
            user_id (str, optional): ID of the user requesting status

        Returns:
            dict: Job status information
        """
        with db.session_scope() as session:
            query = session.query(Task).filter_by(id=job_id)

            # If user_id is provided, restrict to tasks for that user
            if user_id:
                query = query.filter_by(user_id=user_id)

            task = query.first()

            if not task:
                return None

            status = {
                'id': task.id,
                'status': task.status,
                'progress': task.progress,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'started_at': task.started_at.isoformat() if task.started_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None
            }

            # Include result URL for completed tasks
            if task.status == 'completed' and task.result and 'result_path' in task.result:
                # Convert file path to URL
                filename = os.path.basename(task.result['result_path'])
                status['result_url'] = f"/api/results/{filename}"

            # Include error for failed tasks
            if task.status == 'failed' and task.error:
                status['error'] = task.error

            return status

    def cancel_job(self, job_id, user_id):
        """
        Cancel a queued job

        Args:
            job_id (str): ID of the job to cancel
            user_id (str): ID of the user requesting cancellation

        Returns:
            bool: True if job was cancelled, False otherwise
        """
        with db.session_scope() as session:
            task = session.query(Task).filter_by(id=job_id, user_id=user_id).first()

            if not task:
                return False

            if task.status == 'queued':
                task.status = 'cancelled'
                task.completed_at = datetime.utcnow()
                session.commit()
                logger.info(f"Cancelled job {job_id} for user {user_id}")
                return True

            # Cannot cancel jobs that are already processing, completed, or failed
            return False

    def get_user_jobs(self, user_id, status=None, limit=10, offset=0):
        """
        Get jobs for a specific user

        Args:
            user_id (str): ID of the user
            status (str, optional): Filter by status
            limit (int): Maximum number of jobs to return
            offset (int): Offset for pagination

        Returns:
            list: List of job status dictionaries
        """
        with db.session_scope() as session:
            query = session.query(Task).filter_by(user_id=user_id)

            if status:
                query = query.filter_by(status=status)

            query = query.order_by(Task.created_at.desc())
            query = query.limit(limit).offset(offset)

            tasks = query.all()

            result = []
            for task in tasks:
                task_info = {
                    'id': task.id,
                    'type': task.type,
                    'status': task.status,
                    'progress': task.progress,
                    'created_at': task.created_at.isoformat() if task.created_at else None,
                    'completed_at': task.completed_at.isoformat() if task.completed_at else None
                }

                result.append(task_info)

            return result

    def cleanup(self):
        """Clean up resources when shutting down"""
        logger.info("Shutting down task service")
        self.running = False