

from utils import telemetry_wrapper

@telemetry_wrapper(tool="create iccp endpoint")
def run_c():
    print("run_c")