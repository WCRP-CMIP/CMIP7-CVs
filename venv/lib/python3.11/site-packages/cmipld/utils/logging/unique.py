'''
Make a generic logger that can be used in any module.
Supports grouping, unique filtering, and configurable file prefix display.
'''
import logging
import os
import inspect
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.traceback import Traceback
from rich import box


class UniqueErrorFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.seen_messages = set()

    def filter(self, record):
        if record.levelno >= logging.WARNING:
            msg_id = (record.msg, str(record.args))
            if msg_id in self.seen_messages:
                return False
            self.seen_messages.add(msg_id)
        return True


class RichConsoleHandler(logging.Handler):
    def __init__(self, show_filepath: bool = True):
        super().__init__()
        self.console = Console()
        # buffer entries: (levelno, logger_name, formatted_message)
        self.buffer = []
        # last_key: (pathname, levelno, logger_name)
        self.last_key = None
        self.show_filepath = show_filepath

    def emit(self, record):
        try:
            key = (record.pathname, record.levelno, record.name)

            
            msg = self.format(record)
            full_msg = f"- {msg}\n"
            # record.name: logger name

            # Prefix each error-level message with a bullet
            if record.levelno >= logging.ERROR:
                full_msg = f"• {full_msg}"

            # Errors with traceback: flush buffer, print exception panel with name in title
            if record.levelno >= logging.ERROR and record.exc_info:
                self.flush()
                tb = Traceback.from_exception(*record.exc_info, suppress=[__name__])
                title = f"[steelblue] ::{record.name}:: [/] Error"
                self.console.print(Panel(tb, title=title, style="bold red"))
                return

            # If new group key, flush existing
            if key != self.last_key:
                self.flush()

            # Buffer this message
            self.buffer.append((record.levelno, record.name, full_msg))
            self.last_key = key

        except Exception:
            self.handleError(record)

    def flush(self):
        """Flush any buffered messages as a single panel."""
        if not self.buffer:
            return

        levelno, logger_name, _ = self.buffer[0]
        # Join messages, ensuring bullets for errors
        if levelno >= logging.ERROR:
            messages = "\n".join(
                msg if msg.startswith("•") else f"• {msg}"
                for _, _, msg in self.buffer
            )
        else:
            messages = "\n".join(msg for _, _, msg in self.buffer)

        # Determine level label
        label = {
            logging.ERROR: "Error",
            logging.WARNING: "Warning",
            logging.INFO: "Info",
            logging.DEBUG: "Debug",
        }.get(levelno, "Log")

        title = f"::{logger_name}:: {label}"
        style = {
            logging.ERROR: "bold red",
            logging.WARNING: "bold yellow",
            logging.INFO: "bold blue",
            logging.DEBUG: "dim",
        }.get(levelno, "")

        self.console.print(Panel(messages, title=title, style=style, box=box.ROUNDED))
        self.buffer.clear()
        self.last_key = None


class UniqueLogger:
    def __init__(
        self,
        to_file: bool = False,
        log_file: Optional[str] = None,
        show_filepath: bool = True
    ):
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
                formatter = logging.Formatter(
                    '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] %(message)s'
                )
            else:
                handler = RichConsoleHandler(show_filepath=show_filepath)
                # Core message formatting handled in emit
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

    def print(self, *args, **kwargs):
        """Print to the console using the rich console."""
        self.logger.handlers[0].console.print(*args, **kwargs)

# Example usage:
if __name__ == "__main__":
    ul = UniqueLogger(show_filepath=True)
    log = ul.get_logger()

    log.info("First info from full path prefix")
    log.info("Second info from full path prefix")
    log.warning("A warning message")
    log.error("An error occurred")
    log.error("Another error occurred")
    # Flush remaining
    for h in log.handlers:
        if isinstance(h, RichConsoleHandler):
            h.flush()
