import logging
import structlog
import sys

from ansiblereview.display.base import BaseDisplay


class Display(BaseDisplay):
    def __init__(self, name, level=logging.ERROR):
        BaseDisplay.__init__(self, name, level)
        logging.basicConfig(
            format="%(message)s",
            level=level,
            stream=sys.stdout
        )
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

    def get_handler(self):
        return structlog.getLogger(self.name)

    def info(self, msg, **kwargs):
        return self.logger.info(msg, **kwargs)

    def warn(self, msg, **kwargs):
        return self.logger.warn(msg, **kwargs)

    def error(self, msg, **kwargs):
        return self.logger.error(msg, **kwargs)
