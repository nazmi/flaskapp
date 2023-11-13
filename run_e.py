

from utils import log_event, ExitCode

@log_event(tool="Edit config")
def run_e():
    print("run_e")
    raise Exception("run_e exception")
    return ExitCode.SUCCESS