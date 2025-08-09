import os
import sys
import traceback
from logger.custom_logger import CustomLogger
import inspect
from enum import Enum
from typing import Optional , Dict

logger = CustomLogger().get_logger(__file__)

class ExceptionSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DocumentPortalExceptionImproved(Exception):
    """"Custom exception for Document Portal with automatic logging and improved error tracking"""

    def __init__(self, error_message:str, original_exception: Optional[Exception] = None,
                 severity: ExceptionSeverity = ExceptionSeverity.MEDIUM, context : Optional[Dict]=None):
        super().__init__(error_message)
        self.error_message = error_message
        self.original_exception = original_exception
        self.severity = severity
        self.context = context or {}

        self._extract_caller_info()

        self._log_exception()


    def _extract_caller_info(self):
          """Safely extract caller information"""
          try:
              if self.original_exception and hasattr(self.original_exception, '__traceback__'):
                  tb = self.original_exception.__traceback__
                  if tb:
                      self.file_name = tb.tb_frame.f_code.co_filename
                      self.line_no = tb.tb_lineno
                      self.traceback_str = ''.join(traceback.format_exception(
                          type(self.original_exception),
                          self.original_exception,
                          tb
                      ))
                  else:
                      self._get_current_frame_info()
              else:
                  self._get_current_frame_info()
          except Exception:
              # Fallback if frame inspection fails
              self.file_name = "unknown"
              self.line_no = 0
              self.traceback_str = "Traceback unavailable"

    def _get_current_frame_info(self):
          """Get information from current call stack"""
          try:
              import inspect
              frame = inspect.currentframe()
              if frame and frame.f_back and frame.f_back.f_back:
                  caller_frame = frame.f_back.f_back
                  self.file_name = caller_frame.f_code.co_filename
                  self.line_no = caller_frame.f_lineno
                  self.traceback_str = ''.join(traceback.format_stack())
              else:
                  self.file_name = "unknown"
                  self.line_no = 0
                  self.traceback_str = "Stack unavailable"
          except Exception:
              self.file_name = "unknown"
              self.line_no = 0
              self.traceback_str = "Frame inspection failed"

    def _log_exception(self):
          """Automatically log the exception with appropriate severity"""
          try:
              logger = CustomLogger().get_logger(__file__)

              log_data = {
                  "error_message": self.error_message,
                  "file_name": os.path.basename(self.file_name) if self.file_name else "unknown",
                  "line_no": self.line_no,
                  "severity": self.severity.value,
                  "original_exception": str(self.original_exception) if self.original_exception else None,
                  **self.context
              }

              # Log based on severity
              if self.severity in [ExceptionSeverity.CRITICAL, ExceptionSeverity.HIGH]:
                  logger.error("DocumentPortalException occurred", **log_data)
              else:
                  logger.warning("DocumentPortalException occurred", **log_data)

          except Exception:
              # Don't let logging failures break exception handling
              pass

    def __str__(self) -> str:
          base_name = os.path.basename(self.file_name) if self.file_name else "unknown"

          result = f"""
                DocumentPortalException [{self.severity.value.upper()}]
                File: {base_name}:{self.line_no}
                Message: {self.error_message}"""

          if self.original_exception:
              result += f"\nOriginal: {self.original_exception}"

          if self.context:
              result += f"\nContext: {self.context}"

          return result

    def get_details(self) -> dict:
          """Return exception details as a dictionary"""
          return {
              "error_message": self.error_message,
              "file_name": self.file_name,
              "line_no": self.line_no,
              "severity": self.severity.value,
              "original_exception": str(self.original_exception) if self.original_exception else None,
              "context": self.context,
              "traceback": self.traceback_str
          }

  # Convenience functions for common use cases
def raise_critical_error(message: str, original_exception: Exception = None, **context): # type: ignore
      """Raise a critical severity exception"""
      raise DocumentPortalExceptionImproved(
          message,
          original_exception,
          ExceptionSeverity.CRITICAL,
          context
      )

def raise_validation_error(message: str, **context):
      """Raise a validation error with medium severity"""
      raise DocumentPortalExceptionImproved(
          message,
          severity=ExceptionSeverity.MEDIUM,
          context=context
      )
    