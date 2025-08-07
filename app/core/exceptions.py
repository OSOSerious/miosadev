from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class MiosaException(Exception):
    """Base exception for MIOSA application"""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ConsultationNotFoundError(MiosaException):
    """Raised when consultation is not found"""
    def __init__(self, consultation_id: str):
        super().__init__(
            message=f"Consultation {consultation_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class InvalidInputError(MiosaException):
    """Raised when input validation fails"""
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class GroqAPIError(MiosaException):
    """Raised when Groq API call fails"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        details = {"error_code": error_code} if error_code else {}
        super().__init__(
            message=f"Groq API error: {message}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


class RateLimitError(MiosaException):
    """Raised when rate limit is exceeded"""
    def __init__(self, retry_after: Optional[int] = None):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )


class AuthenticationError(MiosaException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationError(MiosaException):
    """Raised when authorization fails"""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


class DatabaseError(MiosaException):
    """Raised when database operation fails"""
    def __init__(self, message: str, operation: Optional[str] = None):
        details = {"operation": operation} if operation else {}
        super().__init__(
            message=f"Database error: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class SessionExpiredError(MiosaException):
    """Raised when session has expired"""
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session {session_id} has expired",
            status_code=status.HTTP_410_GONE
        )


def handle_miosa_exception(exc: MiosaException) -> HTTPException:
    """Convert MiosaException to HTTPException for FastAPI"""
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "message": exc.message,
            "details": exc.details
        }
    )