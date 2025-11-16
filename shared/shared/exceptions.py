"""
Custom exception hierarchy for podcast generation pipeline.

This module defines specific exception types for better error handling,
recovery strategies, and user-facing error messages.
"""

from typing import Optional, Dict, Any


class PodcastGenerationError(Exception):
    """
    Base exception for all podcast generation errors.

    Attributes:
        error_code (str): Machine-readable error code
        message (str): Human-readable error message
        details (Dict): Additional error context
        retry_after (Optional[int]): Seconds to wait before retry
        recoverable (bool): Whether the error is recoverable
    """

    error_code = "PODCAST_000"
    retry_after: Optional[int] = None
    recoverable = False

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        retry_after: Optional[int] = None
    ):
        """
        Initialize the exception.

        Args:
            message (str): Human-readable error message
            details (Optional[Dict]): Additional error context
            retry_after (Optional[int]): Seconds to wait before retry
        """
        self.message = message
        self.details = details or {}
        if retry_after is not None:
            self.retry_after = retry_after
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for API responses.

        Returns:
            Dict: Serializable error information
        """
        result = {
            "error_code": self.error_code,
            "message": self.message,
            "recoverable": self.recoverable,
        }
        if self.details:
            result["details"] = self.details
        if self.retry_after is not None:
            result["retry_after"] = self.retry_after
        return result


# PDF Processing Errors
class PDFProcessingError(PodcastGenerationError):
    """Base exception for PDF processing errors."""
    error_code = "PDF_000"


class PDFNotFoundError(PDFProcessingError):
    """PDF file not found."""
    error_code = "PDF_001"
    recoverable = False


class PDFConversionError(PDFProcessingError):
    """PDF to markdown conversion failed."""
    error_code = "PDF_002"
    recoverable = True
    retry_after = 30


class PDFInvalidFormatError(PDFProcessingError):
    """PDF format is invalid or corrupted."""
    error_code = "PDF_003"
    recoverable = False


class PDFExtractionError(PDFProcessingError):
    """Failed to extract content from PDF."""
    error_code = "PDF_004"
    recoverable = True
    retry_after = 15


# LLM Errors
class LLMError(PodcastGenerationError):
    """Base exception for LLM-related errors."""
    error_code = "LLM_000"


class LLMTimeoutError(LLMError):
    """LLM request timed out."""
    error_code = "LLM_001"
    recoverable = True
    retry_after = 60


class LLMRateLimitError(LLMError):
    """LLM API rate limit exceeded."""
    error_code = "LLM_002"
    recoverable = True
    retry_after = 120


class LLMInvalidResponseError(LLMError):
    """LLM returned invalid or malformed response."""
    error_code = "LLM_003"
    recoverable = True
    retry_after = 30


class LLMQuotaExceededError(LLMError):
    """LLM API quota exceeded."""
    error_code = "LLM_004"
    recoverable = False


class LLMAuthenticationError(LLMError):
    """LLM API authentication failed."""
    error_code = "LLM_005"
    recoverable = False


# TTS Errors
class TTSError(PodcastGenerationError):
    """Base exception for text-to-speech errors."""
    error_code = "TTS_000"


class TTSVoiceNotFoundError(TTSError):
    """Requested voice ID not found."""
    error_code = "TTS_001"
    recoverable = False


class TTSGenerationError(TTSError):
    """Audio generation failed."""
    error_code = "TTS_002"
    recoverable = True
    retry_after = 30


class TTSQuotaExceededError(TTSError):
    """TTS service quota exceeded."""
    error_code = "TTS_003"
    recoverable = False


class TTSRateLimitError(TTSError):
    """TTS service rate limit exceeded."""
    error_code = "TTS_004"
    recoverable = True
    retry_after = 60


# Storage Errors
class StorageError(PodcastGenerationError):
    """Base exception for storage-related errors."""
    error_code = "STORAGE_000"


class StorageUploadError(StorageError):
    """Failed to upload file to storage."""
    error_code = "STORAGE_001"
    recoverable = True
    retry_after = 15


class StorageDownloadError(StorageError):
    """Failed to download file from storage."""
    error_code = "STORAGE_002"
    recoverable = True
    retry_after = 15


class StorageNotFoundError(StorageError):
    """Requested file not found in storage."""
    error_code = "STORAGE_003"
    recoverable = False


class StorageQuotaExceededError(StorageError):
    """Storage quota exceeded."""
    error_code = "STORAGE_004"
    recoverable = False


# Workflow Errors
class WorkflowError(PodcastGenerationError):
    """Base exception for workflow orchestration errors."""
    error_code = "WORKFLOW_000"


class WorkflowTimeoutError(WorkflowError):
    """Workflow exceeded maximum execution time."""
    error_code = "WORKFLOW_001"
    recoverable = False


class WorkflowValidationError(WorkflowError):
    """Workflow input validation failed."""
    error_code = "WORKFLOW_002"
    recoverable = False


class WorkflowStateError(WorkflowError):
    """Invalid workflow state transition."""
    error_code = "WORKFLOW_003"
    recoverable = False


# Validation Errors
class ValidationError(PodcastGenerationError):
    """Base exception for input validation errors."""
    error_code = "VALIDATION_000"
    recoverable = False


class InvalidDurationError(ValidationError):
    """Podcast duration is invalid."""
    error_code = "VALIDATION_001"


class InvalidFileTypeError(ValidationError):
    """File type is not supported."""
    error_code = "VALIDATION_002"


class InvalidParameterError(ValidationError):
    """Invalid parameter value."""
    error_code = "VALIDATION_003"


class FileSizeLimitError(ValidationError):
    """File size exceeds limit."""
    error_code = "VALIDATION_004"


# Resource Errors
class ResourceError(PodcastGenerationError):
    """Base exception for resource management errors."""
    error_code = "RESOURCE_000"


class RateLimitExceededError(ResourceError):
    """User rate limit exceeded."""
    error_code = "RESOURCE_001"
    recoverable = True
    retry_after = 300


class ConcurrentJobLimitError(ResourceError):
    """Maximum concurrent jobs exceeded."""
    error_code = "RESOURCE_002"
    recoverable = True
    retry_after = 60


class QuotaExceededError(ResourceError):
    """User quota exceeded."""
    error_code = "RESOURCE_003"
    recoverable = False


def get_user_friendly_message(error: Exception) -> str:
    """
    Convert technical error to user-friendly message.

    Args:
        error (Exception): The exception to convert

    Returns:
        str: User-friendly error message
    """
    if isinstance(error, PDFNotFoundError):
        return "The PDF file could not be found. Please check the file path and try again."
    elif isinstance(error, PDFConversionError):
        return "We encountered an issue converting your PDF. Please try again in a few moments."
    elif isinstance(error, PDFInvalidFormatError):
        return "The PDF file appears to be corrupted or in an unsupported format."
    elif isinstance(error, LLMTimeoutError):
        return "The AI service is taking longer than expected. Please try again."
    elif isinstance(error, LLMRateLimitError):
        return "We're experiencing high demand. Please wait a few minutes and try again."
    elif isinstance(error, LLMQuotaExceededError):
        return "You've reached your usage limit. Please upgrade your plan or try again later."
    elif isinstance(error, TTSVoiceNotFoundError):
        return "The selected voice is not available. Please choose a different voice."
    elif isinstance(error, TTSQuotaExceededError):
        return "You've reached your audio generation limit for this period."
    elif isinstance(error, StorageQuotaExceededError):
        return "You've reached your storage limit. Please delete some files or upgrade your plan."
    elif isinstance(error, RateLimitExceededError):
        return "You're making requests too quickly. Please wait a few minutes and try again."
    elif isinstance(error, ConcurrentJobLimitError):
        return "You have too many podcasts being generated at once. Please wait for one to complete."
    elif isinstance(error, PodcastGenerationError):
        return error.message
    else:
        return "An unexpected error occurred. Please try again or contact support."
