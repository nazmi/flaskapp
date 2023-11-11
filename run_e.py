

from utils import telemetry_wrapper
@telemetry_wrapper
def run_e():
    print("run_e")
    raise Exception("run_e exception")