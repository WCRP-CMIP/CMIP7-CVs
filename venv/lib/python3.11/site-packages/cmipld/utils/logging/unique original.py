'''
Make a generic logger that can be used in any module.
and link into this one. 
'''
import logging
import os
import inspect
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.traceback import Traceback


class UniqueErrorFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.seen_messages = set()

    def filter(self, record):
        if record.levelno >= logging.WARNING:
            # Convert message and arguments into a string representation for comparison
            msg_id = (record.msg, str(record.args))
            if msg_id in self.seen_messages:
                return False
            self.seen_messages.add(msg_id)
        return True


class RichConsoleHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.console = Console()

    def emit(self, record):
        try:
            
            msg = self.format(record)
            full_msg = f"[violet] ::{record.name}:: [/] {msg}"

            if record.levelno >= logging.ERROR and record.exc_info:
                tb = Traceback.from_exception(*record.exc_info, suppress=[__name__])
                self.console.print(Panel(tb, title=":boom: Error", style="bold red"))
            elif record.levelno >= logging.ERROR:
                self.console.print(Panel(full_msg, title=":boom: Error", style="bold red"))
            elif record.levelno >= logging.WARNING:
                self.console.print(Panel(full_msg, title=":warning: Warning", style="bold yellow"))
            elif record.levelno >= logging.INFO:
                self.console.print(Panel(full_msg, title=":information: Info", style="bold blue"))
            else:
                self.console.print(Panel(full_msg, title="Debug", style="dim"))
        except Exception:
            self.handleError(record)


class UniqueLogger:
    def __init__(self, to_file: bool = False, log_file: Optional[str] = None):
        # Determine calling module name
        frame = inspect.stack()[1]
        module_file = os.path.basename(frame.filename)
        logger_name = os.path.splitext(module_file)[0]

        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        if not self.logger.hasHandlers():
            if to_file:
                handler = logging.FileHandler(log_file or f"{logger_name}.log")
                formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] %(message)s')
            else:
                handler = RichConsoleHandler()
                formatter = logging.Formatter('[%(filename)s:%(lineno)d] %(message)s')

            handler.setFormatter(formatter)
            handler.addFilter(UniqueErrorFilter())
            self.logger.addHandler(handler)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        kwargs.setdefault("exc_info", True)
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        kwargs.setdefault("exc_info", True)
        self.logger.critical(msg, *args, **kwargs)

    def get_logger(self):
        return self.logger
