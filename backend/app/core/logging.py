import logging
import sys
import structlog
from pythonjsonlogger import jsonlogger

class RequestIDFilter(logging.Filter):
    def filter(self, record):
        context = structlog.contextvars.get_contextvars()
        record.request_id = context.get("request_id", "N/A")
        return True

def setup_logging():
    # Очищаем корневой логгер
    root = logging.getLogger()
    root.handlers.clear()

    # Создаём общий обработчик с JSON
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )
    handler.setFormatter(formatter)
    handler.addFilter(RequestIDFilter())

    # Вешаем на корневой логгер и на все нужные логгеры
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    # Логгеры, которые должны обязательно использовать наш обработчик
    for name in ["uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy.engine"]:
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.propagate = True  # теперь сообщения попадут в корневой логгер
        # и, соответственно, в handler с JSON
        logger.setLevel(logging.INFO)

    # Настройка structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def get_logger(name: str = __name__):
    return structlog.get_logger(name)