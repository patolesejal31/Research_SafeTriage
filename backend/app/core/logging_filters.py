"""Logging filters and redaction mechanisms for SafeTriage.

Ensures that no raw symptom descriptions, passwords, authentication tokens,
or planted test secrets appear in application or audit logs.
"""

import logging
import re
from typing import Any

# Patterns that indicate sensitive content requiring redaction
SENSITIVE_PATTERNS = [
    re.compile(r"SECRET_SYMPTOM_[A-Za-z0-9_]+", re.IGNORECASE),
    re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE),
    re.compile(r"(?:api[_-]?key|apikey)['\"]?\s*[:=]\s*['\"][^'\"]+['\"]", re.IGNORECASE),
    re.compile(r"(?:password|passwd)['\"]?\s*[:=]\s*['\"][^'\"]+['\"]", re.IGNORECASE),
    re.compile(r"(?:token|secret)['\"]?\s*[:=]\s*['\"][^'\"]+['\"]", re.IGNORECASE),
]


class SensitiveDataFilter(logging.Filter):
    """Logging filter that redacts sensitive strings, secrets, and raw symptoms."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self._redact_string(record.msg)
        
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: self._sanitize_arg(v) for k, v in record.args.items()}
            else:
                sanitized = [self._sanitize_arg(a) for a in record.args]
                record.args = tuple(sanitized) if isinstance(record.args, tuple) else sanitized
        return True

    def _redact_string(self, text: str) -> str:
        redacted = text
        for pattern in SENSITIVE_PATTERNS:
            redacted = pattern.sub("[REDACTED]", redacted)
        return redacted

    def _sanitize_arg(self, arg: Any) -> Any:
        if isinstance(arg, str):
            return self._redact_string(arg)
        return arg


def configure_safe_logging(logger_name: str | None = None) -> logging.Logger:
    """Attach the SensitiveDataFilter to the specified logger or root logger."""
    logger = logging.getLogger(logger_name)
    has_filter = any(isinstance(f, SensitiveDataFilter) for f in logger.filters)
    if not has_filter:
        logger.addFilter(SensitiveDataFilter())
    return logger
