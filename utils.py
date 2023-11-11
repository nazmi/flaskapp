import atexit
import json
import os
import datetime
import socket
import sys
import uuid

class Telemetry:
    _instance = None
    _correlation_id = None
    _commit_version = None
    _project_name = None
    _host = None
    _args = None
    _cwd = None
    log_entries = []

    def __new__(cls,**config):
        if cls._instance is None:
            # init the instance
            cls._instance = super(Telemetry, cls).__new__(cls)

            # init all the properties
            cls._correlation_id = str(uuid.uuid4())
            cls._commit_version = config.get('commit_version', 'Unknown')
            cls._project_name = config.get('project_name', 'Unknown')
            cls._host = socket.gethostname()
            cls._args = sys.argv
            cls._args[0] = os.path.basename(cls._args[0])
            cls._cwd = os.getcwd() + os.sep

            # write to logs on exit
            atexit.register(cls._instance.write_logs_to_file)
        return cls._instance

    def log_action(self, func, **kwargs):
        log_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "host": self._host,
            "run_id": self._correlation_id,
            "args": self._args,
            "project": self._project_name,
            "commit": self._commit_version,
            "file": os.path.basename(func.__code__.co_filename),
            "func": func.__name__,
            "tool": kwargs.get('tool', func.__name__),
            "exception": kwargs.get('exception', False)
        }
        self.log_entries.append(log_entry)

    def write_logs_to_file(self):
        log_directory = os.path.join(os.getcwd(),'logs')
        os.makedirs(log_directory, exist_ok=True)
        log_filename = f"{self._project_name}.log"
        log_file_path = os.path.join(log_directory, log_filename)
        
        with open(log_file_path, 'a') as log_file:
            for entry in self.log_entries:
                log_file.write(json.dumps(entry) + "\n")

        # Clear log entries after writing
        self.log_entries.clear()


from functools import wraps

def telemetry_wrapper(_func=None, **decorator_kwargs):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except BaseException as e:
                decorator_kwargs['exception'] = {
                    "name": type(e).__name__,
                    "message": str(e),
                }
                raise
            finally:
                Telemetry().log_action(func, **decorator_kwargs)
            return result
        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)