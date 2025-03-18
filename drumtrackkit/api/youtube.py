import os
import uuid
import logging
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import validators
from werkzeug.exceptions import BadRequest, Unauthorized
# Removed PaymentRequired import

from drumtrackkit.services.youtube_service import YouTubeService
from drumtrackkit.services.analysis_service import AnalysisService
from drumtrackkit.services.task_service import TaskService
from drumtrackkit.models.user import User
from drumtrackkit.models.analysis import Analysis
from drumtrackkit import db

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
youtube_bp = Blueprint('youtube', __name__, url_prefix='/api/youtube')

# Initialize services
youtube_service = YouTubeService()
analysis_service = AnalysisService()
task_service = TaskService()


@youtube_bp.route('/search', methods=['POST'])
@jwt_required()
def search_videos():
    """
    Search YouTube for drum performance videos

    Request:
    {
        "query": "Steve Gadd drum solo",
        "max_results": 20
    }

    Response:
    {
        "results": [
            {
                "id": "video_id",
                "title": "Video title",
                "thumbnail": "thumbnail_url",
                "channel": "Channel name",
                "duration": 180
            }
        ]
    }
    """
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 401

        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validate query
        query = data.get('query')
        if not query or not isinstance(query, str) or len(query.strip()) == 0:
            return jsonify({"error": "Valid search query is required"}), 400

        # Get max results (with validation)
        max_results = data.get('max_results', 20)
        try:
            max_results = int(max_results)
            max_results = min(max_results, 50)  # Limit to 50
            max_results = max(max_results, 1)  # Minimum of 1
        except (ValueError, TypeError):
            max_results = 20  # Default

        # Log search request
        logger.info(f"YouTube search request: query='{query}', max_results={max_results}, user_id={current_user_id}")

        # Perform search
        results = youtube_service.search_videos(query, max_results)

        return jsonify({"results": results}), 200

    except Exception as e:
        logger.error(f"Error in YouTube search: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while searching YouTube"}), 500


@youtube_bp.route('/download', methods=['POST'])
@jwt_required()
def download_video():
    """
    Download YouTube video for analysis

    Request:
    {
        "url": "https://www.youtube.com/watch?v=video_id",
        "start_time": 0,
        "duration": 180,
        "analysis_type": "performance"
    }

    Response:
    {
        "job_id": "uuid",
        "status": "queued",
        "progress": 0
    }
    """
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 401

        # Check user credits
        if user.subscription_tier == 'free' and user.credits_remaining <= 0:
            # Changed from raising PaymentRequired to returning a response
            return jsonify({
                "error": "You have used all your free credits",
                "code": "insufficient_credits",
                "details": {
                    "subscription_tier": user.subscription_tier,
                    "credits_remaining": user.credits_remaining
                }
            }), 402

        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validate URL
        url = data.get('url')
        if not url or not isinstance(url, str):
            return jsonify({"error": "YouTube URL is required"}), 400

        # Validate URL format
        if not validators.url(url) or 'youtube.com' not in url and 'youtu.be' not in url:
            return jsonify({"error": "Invalid YouTube URL"}), 400

        # Get optional parameters
        start_time = data.get('start_time', 0)
        duration = data.get('duration', 180)
        analysis_type = data.get('analysis_type', 'performance')

        # Validate parameters
        try:
            start_time = int(start_time)
            start_time = max(start_time, 0)
        except (ValueError, TypeError):
            start_time = 0

        try:
            duration = int(duration)
            duration = min(duration, 300)  # Max 5 minutes
            duration = max(duration, 10)  # Min 10 seconds
        except (ValueError, TypeError):
            duration = 180

        if analysis_type not in ['performance', 'training', 'reference']:
            analysis_type = 'performance'

        # Create analysis record
        analysis = Analysis(
            user_id=current_user_id,
            analysis_type='youtube',
            status='queued',
            parameters={
                'url': url,
                'start_time': start_time,
                'duration': duration,
                'analysis_type': analysis_type
            }
        )
        db.session.add(analysis)
        db.session.commit()

        # Create task for background processing
        job_id = task_service.create_job(
            job_type='youtube_analysis',
            parameters={
                'analysis_id': analysis.id,
                'url': url,
                'start_time': start_time,
                'duration': duration,
                'analysis_type': analysis_type
            },
            user_id=current_user_id
        )

        # Update analysis record with job_id
        analysis.job_id = job_id
        db.session.commit()

        # Deduct credits for free tier users
        if user.subscription_tier == 'free':
            user.credits_remaining -= 1
            db.session.commit()

        # Log task creation
        logger.info(
            f"YouTube analysis task created: job_id={job_id}, analysis_id={analysis.id}, user_id={current_user_id}")

        # Return job status
        return jsonify({
            "job_id": job_id,
            "status": "queued",
            "progress": 0
        }), 202

    except Exception as e:
        logger.error(f"Error in YouTube download: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while processing your request"}), 500


@youtube_bp.route('/status/<job_id>', methods=['GET'])
@jwt_required()
def get_job_status(job_id):
    """
    Get the status of a YouTube analysis job

    Response:
    {
        "id": "job_id",
        "status": "processing",
        "progress": 50,
        "result_url": null,
        "error": null
    }
    """
    try:
        # Get current user
        current_user_id = get_jwt_identity()

        # Validate job_id format
        try:
            uuid_obj = uuid.UUID(job_id)
        except ValueError:
            return jsonify({"error": "Invalid job ID format"}), 400

        # Get job status
        job_status = task_service.get_job_status(job_id, current_user_id)
        if not job_status:
            return jsonify({"error": "Job not found or access denied"}), 404

        return jsonify(job_status), 200

    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while getting job status"}), 500
    