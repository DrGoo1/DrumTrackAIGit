import logging
import traceback
from flask import Blueprint, jsonify, current_app, request
from werkzeug.exceptions import HTTPException
from drumtrackkit.utils.exceptions import (
    DrumTrackAIError, ResourceNotFoundError, ValidationError,
    AuthenticationError, AuthorizationError, PaymentRequiredError,
    ServiceUnavailableError
)

# Set up logging
logger = logging.getLogger(__name__)

error_bp = Blueprint('errors', __name__)


@error_bp.app_errorhandler(Exception)
def handle_exception(e):
    """Handle all unhandled exceptions"""
    # Log the error
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)

    # Default response
    response = {
        "error": {
            "code": "internal_server_error",
            "message": "An unexpected error occurred"
        }
    }
    status_code = 500

    # Custom DrumTrackAI exceptions
    if isinstance(e, DrumTrackAIError):
        response["error"]["code"] = e.code or "application_error"
        response["error"]["message"] = e.message

        # Map exception types to status codes
        if isinstance(e, ResourceNotFoundError):
            status_code = 404
        elif isinstance(e, ValidationError):
            status_code = 400
            # Add field-specific error details if available
            if hasattr(e, 'field') and e.field:
                response["error"]["field"] = e.field
            if hasattr(e, 'details') and e.details:
                response["error"]["details"] = e.details
        elif isinstance(e, AuthenticationError):
            status_code = 401
        elif isinstance(e, AuthorizationError):
            status_code = 403
        elif isinstance(e, PaymentRequiredError):
            status_code = 402
        elif isinstance(e, ServiceUnavailableError):
            status_code = 503
        else:
            status_code = 500

    # Handle Werkzeug HTTP exceptions
    elif isinstance(e, HTTPException):
        status_code = e.code
        response["error"]["code"] = str(e.name).lower().replace(' ', '_')
        response["error"]["message"] = e.description

    # Include stack trace in development mode
    if current_app.config.get('DEBUG', False):
        response["error"]["stack_trace"] = traceback.format_exc()

    # Add request information in development mode
    if current_app.config.get('DEBUG', False):
        response["error"]["request"] = {
            "url": request.url,
            "method": request.method,
            "headers": dict(request.headers),
            "args": dict(request.args),
            "form": dict(request.form) if request.form else None,
            "json": request.json if request.is_json else None
        }

    return jsonify(response), status_code


# Register specific error handlers
@error_bp.app_errorhandler(400)
def bad_request(e):
    """Handle 400 Bad Request errors"""
    return jsonify({
        "error": {
            "code": "bad_request",
            "message": str(e) or "Bad request"
        }
    }), 400


@error_bp.app_errorhandler(401)
def unauthorized(e):
    """Handle 401 Unauthorized errors"""
    return jsonify({
        "error": {
            "code": "unauthorized",
            "message": str(e) or "Authentication required"
        }
    }), 401


@error_bp.app_errorhandler(403)
def forbidden(e):
    """Handle 403 Forbidden errors"""
    return jsonify({
        "error": {
            "code": "forbidden",
            "message": str(e) or "Access forbidden"
        }
    }), 403


@error_bp.app_errorhandler(404)
def not_found(e):
    """Handle 404 Not Found errors"""
    return jsonify({
        "error": {
            "code": "not_found",
            "message": str(e) or "Resource not found"
        }
    }), 404


@error_bp.app_errorhandler(405)
def method_not_allowed(e):
    """Handle 405 Method Not Allowed errors"""
    return jsonify({
        "error": {
            "code": "method_not_allowed",
            "message": str(e) or "Method not allowed"
        }
    }), 405


@error_bp.app_errorhandler(429)
def too_many_requests(e):
    """Handle 429 Too Many Requests errors"""
    return jsonify({
        "error": {
            "code": "rate_limit_exceeded",
            "message": str(e) or "Too many requests, please try again later"
        }
    }), 429


@error_bp.app_errorhandler(500)
def internal_server_error(e):
    """Handle 500 Internal Server Error errors"""
    logger.error(f"Internal server error: {str(e)}", exc_info=True)
    return jsonify({
        "error": {
            "code": "internal_server_error",
            "message": "An unexpected error occurred"
        }
    }), 500


def register_error_handlers(app):
    """Register error handlers with the Flask app"""
    app.register_blueprint(error_bp)