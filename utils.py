import atexit
import json
import os
import socket
import sys
import uuid
from collections import defaultdict
from datetime import datetime
from operator import itemgetter
from functools import wraps

class ExitCode:
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    EARLY_RETURN = "EARLY_RETURN"
    UNKNOWN = "UNKNOWN"

class Telemetry:
    _instance = None
    _correlation_id = None
    _commit_version = None
    _project_name = None
    _host = None
    _args = None
    _cwd = None
    _log_dir = None
    _log_file = None
    log_entries = []

    def __new__(cls,**config):
        if cls._instance is None:
            # init the instance
            cls._instance = super(Telemetry, cls).__new__(cls)

            # init all the properties
            cls._correlation_id = uuid.uuid4().hex
            cls._commit_version = config.get('commit_version', 'Unknown')
            cls._project_name = config.get('project_name', 'Unknown')
            cls._host = socket.gethostname()
            cls._args = sys.argv
            cls._args[0] = os.path.basename(cls._args[0])
            cls._cwd = os.getcwd()
            cls._log_dir = os.path.join(cls._cwd, 'logs')
            cls._log_file = os.path.join(cls._log_dir, f"{cls._project_name}.log")
            
            # write to logs on exit
            # write html report on exit
            atexit.register(cls._terminate, cls._instance)
        return cls._instance

    def log_action(self, func, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "host": self._host,
            "run_id": self._correlation_id,
            "args": self._args,
            "project": self._project_name,
            "commit": self._commit_version,
            "file": os.path.basename(func.__code__.co_filename),
            "func": func.__name__,
            "tool": kwargs.get('tool', func.__name__),
            "exit_code": kwargs.get('exit_code', ExitCode.UNKNOWN),
            "exception": kwargs.get('exception', None)
        }
        self.log_entries.append(log_entry)

    def _terminate(self):

        self._write_logs_to_file()
        self._write_html_report()
        return

    def _write_logs_to_file(self):
        os.makedirs(self._log_dir, exist_ok=True)
        with open(self._log_file, 'a') as log_file:
            for entry in self.log_entries:
                log_file.write(json.dumps(entry) + "\n")

        # Clear log entries after writing
        self.log_entries.clear()

    def _write_html_report(self):
        """Aggregates logs into an HTML report"""

        logs = []

        with open(self._log_file, 'r') as file:
            logs.extend([json.loads(line) for line in file])

        # Filter out logs with exceptions and sort by timestamp
        logs_no_exceptions = sorted(
            (log for log in logs if log.get('exception') is None and log.get('exit_code') == ExitCode.SUCCESS),
            key=itemgetter('timestamp'), reverse=True
        )

        # Aggregate logs by project, then by tool, picking only the latest run
        latest_runs_per_project = defaultdict(dict)
        for log in logs_no_exceptions:
            project = log['project']
            tool = log['tool']
            # Update the record if this tool has no entry or if the log is more recent
            if tool not in latest_runs_per_project[project]:
                latest_runs_per_project[project][tool] = log
        
        # Placeholder for latest runs rows
        latest_runs_rows = ''
        for project, tools in latest_runs_per_project.items():
            for tool_log in sorted(tools.values(), key=itemgetter('timestamp'), reverse=True):
                latest_runs_rows += f"<tr><td>{tool_log['timestamp']}</td><td>{tool_log['run_id'][0:6]}</td><td>{tool_log['host']}</td><td>{tool_log['commit'][0:6]}</td><td>{project}</td><td>{tool_log['tool']}</td></tr>"

        # Group logs by run_id
        history_by_run_id = defaultdict(list)
        for log in logs:
            history_by_run_id[log['run_id']].append(log)

        # Sort groups by the first timestamp in each group
        sorted_history = sorted(history_by_run_id.values(), key=lambda x: x[0]['timestamp'])
        sorted_history.reverse()

        # Placeholder for history diagram rows
        history_diagram_rows = ''
        for group in sorted_history:
            timestamp = group[0]['timestamp']
            hostname = group[0]['host']
            commit = group[0]['commit'][0:6]
            project = group[0]['project']
            run_id = group[0]['run_id'][0:6]
            run_sequence = "<br/>".join(f"{log['tool']} ({log['exit_code']})" for log in group)
            history_diagram_rows += f"<tr><td>{timestamp}</td><td>{run_id}</td><td>{hostname}</td><td>{commit}</td><td>{project}</td><td>{run_sequence}</td></tr>"


        # Read the template content
        with open('template.html', 'r') as file:
            html_template = file.read()

        # Replace placeholders in the template with actual content
        current_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        final_html_content = html_template.replace('<!-- Latest Runs Rows -->', latest_runs_rows)
        final_html_content = final_html_content.replace('<!-- History Diagram Rows -->', history_diagram_rows)
        final_html_content = final_html_content.replace('<!-- Log File Path -->', self._log_file)
        final_html_content = final_html_content.replace('<!-- Date Created -->', current_time)

        # Write the final HTML content to a new file
        output_file_path = os.path.join(self._log_dir, self._log_file+'.html')
        with open(output_file_path, 'w') as html_file:
            html_file.write(final_html_content)

        print(f"HTML log report has been generated: {output_file_path}")



def log_event(_func=None, **decorator_kwargs):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            try:
                result = func(*args, **kwargs)
            except BaseException as e:
                decorator_kwargs['exception'] = {
                    "name": type(e).__name__,
                    "message": str(e),
                }
                result = False
                raise
            finally:

                if result is None:
                    decorator_kwargs['exit_code'] = ExitCode.EARLY_RETURN
                elif result:
                    decorator_kwargs['exit_code'] = ExitCode.SUCCESS
                else:
                    decorator_kwargs['exit_code'] = ExitCode.FAILURE

                Telemetry().log_action(func, **decorator_kwargs)
            return result
        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)

import win32api
#==============================================================================
def getFileProperties(fname):
#==============================================================================
    """
    Read all properties of the given file return them as a dictionary.
    """
    propNames = ('Comments', 'InternalName', 'ProductName',
        'CompanyName', 'LegalCopyright', 'ProductVersion',
        'FileDescription', 'LegalTrademarks', 'PrivateBuild',
        'FileVersion', 'OriginalFilename', 'SpecialBuild')

    props = {'FixedFileInfo': None, 'StringFileInfo': None, 'FileVersion': None}

    try:
        # backslash as parm returns dictionary of numeric info corresponding to VS_FIXEDFILEINFO struc
        fixedInfo = win32api.GetFileVersionInfo(fname, '\\')
        props['FixedFileInfo'] = fixedInfo
        props['FileVersion'] = "%d.%d.%d.%d" % (fixedInfo['FileVersionMS'] / 65536,
                fixedInfo['FileVersionMS'] % 65536, fixedInfo['FileVersionLS'] / 65536,
                fixedInfo['FileVersionLS'] % 65536)

        # \VarFileInfo\Translation returns list of available (language, codepage)
        # pairs that can be used to retreive string info. We are using only the first pair.
        lang, codepage = win32api.GetFileVersionInfo(fname, '\\VarFileInfo\\Translation')[0]

        # any other must be of the form \StringfileInfo\%04X%04X\parm_name, middle
        # two are language/codepage pair returned from above

        strInfo = {}
        for propName in propNames:
            strInfoPath = u'\\StringFileInfo\\%04X%04X\\%s' % (lang, codepage, propName)
            ## print str_info
            strInfo[propName] = win32api.GetFileVersionInfo(fname, strInfoPath)

        props['StringFileInfo'] = strInfo
    except:
        pass

    return props