import logging
import sys
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Optional


class DockerFileHandler(logging.FileHandler):
    """Особый обработчик для Docker с принудительной синхронизацией"""
    
    def __init__(self, filename, mode='a', encoding=None, delay=False):
        log_dir = os.path.dirname(filename)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        super().__init__(filename, mode, encoding, delay)
    
    def emit(self, record):
        """Переопределяем метод для принудительной записи на диск"""
        super().emit(record)
        self.flush()
        os.fsync(self.stream.fileno())


def setup_logging(log_to_file: bool = True, log_level: Optional[str] = None) -> logging.Logger:
    """
    Настройка логирования с записью в файл и консоль
    
    Args:
        log_to_file: Записывать ли логи в файл
        log_level: Уровень логирования
    """
    from src.core.config import settings
    
    if not log_level:
        log_level = "DEBUG" if settings.MODE == "DEV" else "INFO"
    
    logger = logging.getLogger("url_shortener")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    if logger.handlers:
        logger.handlers.clear()
    
    formatter = logging.Formatter(
        '%(levelname)s:     %(asctime)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%d.%m.%Y %H:%M:%S'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logger.level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_to_file:
        log_dir = Path("/app/logs")
        log_dir.mkdir(exist_ok=True)
        
        main_log_path = log_dir / "app.log"
        
        file_handler = RotatingFileHandler(
            main_log_path,
            maxBytes=10_485_760,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        error_log_path = log_dir / "error.log"
        error_handler = RotatingFileHandler(
            error_log_path,
            maxBytes=10_485_760,
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
        
        if settings.MODE == "PROD":
            time_handler = TimedRotatingFileHandler(
                log_dir / "app.log",
                when="midnight",
                interval=1,
                backupCount=30,
                encoding='utf-8'
            )
            time_handler.setLevel(logging.INFO)
            time_handler.setFormatter(formatter)
            logger.addHandler(time_handler)
        
        logger.info(f"📁 Логи будут сохраняться в: {main_log_path}")
        logger.info(f"📁 Ошибки будут сохраняться в: {error_log_path}")
    
    return logger


logger = setup_logging(log_to_file=True)
