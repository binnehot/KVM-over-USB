import datetime
import os
import sys
import traceback

ARGV_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))


def error_log(msg):
    with open(os.path.join(ARGV_PATH, "error.log"), "w") as f:
        f.write(f"Error Occurred at {datetime.datetime.now()}:\n")
        f.write(f"{msg}\n")


if __name__ == "__main__":
    try:
        from main import main

        return_code = main()
        sys.exit(return_code)
    except Exception:
        error_log(traceback.format_exc())
        sys.exit(1)
