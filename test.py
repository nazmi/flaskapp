from utils import Telemetry, telemetry_wrapper
from run_c import run_c
from run_d import run_d
from run_e import run_e
from run_b_file import run_b
import time
# Example usage of the decorator
def run():
    
    
    for i in range(100):
        time.sleep(0.1)
        match i % 5:
            case 0:
                print("1")
                run_a()
            case 1:
                print("2")
                run_b()
            case 2:
                print("3")
                run_c()
            case 3:
                print("4")
                run_d()
            case 4:
                print("5")
                run_e()
            case _:
                pass

@telemetry_wrapper
def run_a():
    print("run_a")


def main(**config):
    Telemetry(**config)
    run()



if __name__ == '__main__':
    config = {
        "project_name": "test",
        "commit_version": "cad2344as",
    }
    main(**config)
