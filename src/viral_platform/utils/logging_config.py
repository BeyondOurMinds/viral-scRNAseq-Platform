import logging
from collections import deque


_LOG_BUFFER_MAX_LINES = 10000
_log_line_buffer = deque(maxlen=_LOG_BUFFER_MAX_LINES)


class InMemoryLogCaptureHandler(logging.Handler):
    """Capture formatted log lines so they can be exported on demand."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            line = self.format(record)
        except Exception:
            line = record.getMessage()
        _log_line_buffer.append(line)


def get_captured_logs_text() -> str:
    """Return captured project log lines joined as text."""
    return "\n".join(_log_line_buffer)


def clear_captured_logs() -> None:
    """Reset captured log lines (useful for tests)."""
    _log_line_buffer.clear()


def _has_capture_handler(root_logger: logging.Logger) -> bool:
    return any(isinstance(handler, InMemoryLogCaptureHandler) for handler in root_logger.handlers)


def configure_logging(level: int = logging.INFO) -> None:
    root_logger = logging.getLogger()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    if not root_logger.handlers:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler)

    root_logger.setLevel(level)

    if not _has_capture_handler(root_logger):
        capture_handler = InMemoryLogCaptureHandler()
        capture_handler.setLevel(level)
        capture_handler.setFormatter(formatter)
        root_logger.addHandler(capture_handler)
