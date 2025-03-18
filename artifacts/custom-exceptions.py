class DrumTrackAIError(Exception):
    """Base exception class for DrumTrackAI application"""
    def __init__(self, message="An error occurred", code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)

class ResourceNotFoundError(DrumTrackAIError):
    """Exception raised when a requested resource is not found"""
    def __init__(self, message="Resource not found", code="resource_not_found"):
        super().__init__(message, code)

class ValidationError(DrumTrackAIError):
    """Exception raised when input validation fails"""
    def __init__(self, message="Validation error", code="validation_error", field=None, details=None):
        self.field = field
        self.details = details
        super().__init__(message, code)

class AuthenticationError(DrumTrackAIError):
    """Exception raised for authentication failures"""
    def __init__(self, message="Authentication failed", code="authentication_error"):
        super().__init__(message, code)

class AuthorizationError(DrumTrackAIError):
    """Exception raised when a user lacks permission for an action"""
    def __init__(self, message="Not authorized", code="authorization_error"):
        super().__init__(message, code)

class PaymentRequiredError(DrumTrackAIError):
    """Exception raised when a user needs to pay for access"""
    def __init__(self, message="Payment required", code="payment_required"):
        super().__init__(message, code)

class ServiceUnavailableError(DrumTrackAIError):
    """Exception raised when an external service is unavailable"""
    def __init__(self, message="Service unavailable", code="service_unavailable"):
        super().__init__(message, code)

class FileProcessingError(DrumTrackAIError):
    """Exception raised when file processing fails"""
    def __init__(self, message="Error processing file", code="file_processing_error"):
        super().__init__(message, code)

class AudioAnalysisError(DrumTrackAIError):
    """Exception raised when audio analysis fails"""
    def __init__(self, message="Error analyzing audio", code="audio_analysis_error"):
        super().__init__(message, code)

class MIDIProcessingError(DrumTrackAIError):
    """Exception raised when MIDI processing fails"""
    def __init__(self, message="Error processing MIDI", code="midi_processing_error"):
        super().__init__(message, code)

class YouTubeError(DrumTrackAIError):
    """Exception raised for YouTube-related errors"""
    def __init__(self, message="YouTube operation failed", code="youtube_error"):
        super().__init__(message, code)

class DatabaseError(DrumTrackAIError):
    """Exception raised for database-related errors"""
    def __init__(self, message="Database operation failed", code="database_error"):
        super().__init__(message, code)

class ConfigurationError(DrumTrackAIError):
    """Exception raised for configuration-related errors"""
    def __init__(self, message="Configuration error", code="configuration_error"):
        super().__init__(message, code)

class RateLimitExceededError(DrumTrackAIError):
    """Exception raised when rate limit is exceeded"""
    def __init__(self, message="Rate limit exceeded", code="rate_limit_exceeded"):
        super().__init__(message, code)

class CreditLimitExceededError(DrumTrackAIError):
    """Exception raised when user's credit limit is exceeded"""
    def __init__(self, message="Credit limit exceeded", code="credit_limit_exceeded"):
        super().__init__(message, code)