import logging
from django.utils.module_loading import import_string

class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        try:
            # Delay import until handler is used
            LogEntry = import_string("blog.models.LogEntry")
            LogEntry.objects.create(
                level=record.levelname,
                message=record.getMessage(),
                logger_name=record.name,
            )
        except Exception:
            pass  
