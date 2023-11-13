
from utils import log_event, ExitCode


@log_event(tool="Run tests")
def run_b():
    print("run_b")
    return ExitCode.SUCCESS
