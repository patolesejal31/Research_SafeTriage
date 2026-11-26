"""Tests for sensitive data filtering and logger redaction."""

import logging

from app.core.logging_filters import SensitiveDataFilter, configure_safe_logging


class TestLoggingFilters:
    """Tests covering redaction of secrets and symptom data in logging."""

    def test_redact_patterns_in_message(self):
        """Patterns like SECRET_SYMPTOM_*, tokens, passwords, and API keys are redacted."""
        filter_ = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg="User with Bearer eyJhbGciOi... and password='secret_pwd' had SECRET_SYMPTOM_DYSPNEA and api-key='key123'",
            args=(),
            exc_info=None,
        )

        filter_.filter(record)
        assert "SECRET_SYMPTOM" not in record.msg
        assert "eyJhbGciOi" not in record.msg
        assert "secret_pwd" not in record.msg
        assert "key123" not in record.msg
        assert "[REDACTED]" in record.msg

    def test_redact_arguments_tuple(self):
        """Filter handles tuple args containing strings and non-strings."""
        filter_ = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg="Arg test: %s and %d",
            args=("SECRET_SYMPTOM_FEVER", 42),
            exc_info=None,
        )

        filter_.filter(record)
        assert record.args[0] == "[REDACTED]"
        assert record.args[1] == 42

    def test_redact_arguments_dict(self):
        """Filter handles dict args containing strings and non-strings."""
        filter_ = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg="Dict test: %(symptom)s and %(count)d",
            args={"symptom": "SECRET_SYMPTOM_COUGH", "count": 10},
            exc_info=None,
        )

        filter_.filter(record)
        assert record.args["symptom"] == "[REDACTED]"
        assert record.args["count"] == 10

    def test_redact_arguments_list(self):
        """Filter handles list args containing strings and non-strings."""
        filter_ = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg="List test",
            args=["SECRET_SYMPTOM_RASH", 99],
            exc_info=None,
        )

        filter_.filter(record)
        assert record.args[0] == "[REDACTED]"
        assert record.args[1] == 99

    def test_non_string_message(self):
        """Filter passes through non-string record.msg safely."""
        filter_ = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg=12345,  # Non-string
            args=(),
            exc_info=None,
        )

        filter_.filter(record)
        assert record.msg == 12345

    def test_configure_safe_logging_idempotence(self):
        """configure_safe_logging adds filter without duplicating."""
        logger_name = "safetriage.test.config"
        logger = configure_safe_logging(logger_name)
        filters_count = sum(1 for f in logger.filters if isinstance(f, SensitiveDataFilter))
        assert filters_count == 1

        # Calling again should not add a duplicate filter
        configure_safe_logging(logger_name)
        filters_count = sum(1 for f in logger.filters if isinstance(f, SensitiveDataFilter))
        assert filters_count == 1
