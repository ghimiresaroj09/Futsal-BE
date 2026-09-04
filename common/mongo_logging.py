"""MongoDB logging handler used by production deployments.

Logging must never make an API request fail, so write errors are swallowed after
delegating them to ``logging.Handler.handleError``.
"""

from __future__ import annotations

import logging
import socket
from datetime import datetime, timezone
from typing import Any

from pymongo import MongoClient


class MongoDBHandler(logging.Handler):
    """Write structured Python log records to a MongoDB collection."""

    def __init__(
        self,
        uri: str,
        database: str,
        collection: str = "application_logs",
        environment: str = "production",
        timeout_ms: int = 2_000,
    ) -> None:
        super().__init__()
        self.environment = environment
        self.hostname = socket.gethostname()
        self.collection = MongoClient(
            uri,
            connect=False,
            serverSelectionTimeoutMS=timeout_ms,
            connectTimeoutMS=timeout_ms,
        )[database][collection]

    def emit(self, record: logging.LogRecord) -> None:
        try:
            document: dict[str, Any] = {
                "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc),
                "level": record.levelname,
                "logger": record.name,
                "message": self.format(record),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "process": record.process,
                "hostname": self.hostname,
                "environment": self.environment,
            }
            if record.exc_info:
                document["exception"] = logging.Formatter().formatException(record.exc_info)
            self.collection.insert_one(document)
        except Exception:
            self.handleError(record)
