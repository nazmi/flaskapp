from utils import Telemetry, log_event,ExitCode
from run_c import rundasdasdasdasdsadasdasdasdsafef_c
from run_d import rundasdasdasdasdsadasdasdasdsafef_d
from run_e import run_e
from run_b_file import run_b
import time
import sys
import os
import random
# Example usage of the decorator
def run():
    
    n = random.randint(1, 18)
    for _ in range(n):
        time.sleep(0.2)
        i = random.randint(0, 100)
        try:
            match i % 5:
                case 0:
                    print("1")
                    run_a()
                case 1:
                    print("2")
                    run_b()
                case 2:
                    print("3")
                    rundasdasdasdasdsadasdasdasdsafef_c()
                case 3:
                    print("4")
                    rundasdasdasdasdsadasdasdasdsafef_d()
                case 4:
                    print("5")
                    run_e()
                case _:
                    pass
        except Exception as e:
            pass

@log_event
def run_a():
    print("run_a")



def main(**config):
    Telemetry(**config)
    run()


is_nuitka = "__compiled__" in globals()

def get_commit_version():

    if not is_nuitka:
        import subprocess
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    else:
        from utils import getFileProperties
        print(os.path.abspath(sys.argv[0]))
        props = getFileProperties(os.path.abspath(sys.argv[0]))
        return props["StringFileInfo"]["ProductName"]

if __name__ == '__main__':
    config = {
        "project_name": "new branch",
        "commit_version": get_commit_version(),
    }
    main(**config)
