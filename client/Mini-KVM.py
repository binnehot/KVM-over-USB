import datetime
import os
import sys
import traceback

ARGV_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))


def error_log(msg):
    with open(os.path.join(ARGV_PATH, "error.log"), "w") as f:
        f.write(f"Error Occurred at {datetime.datetime.now()}:\n")
        f.write(f"{msg}\n")


try:
    from main import main

    main()
except Exception:
    error_log(traceback.format_exc())
    sys.exit(1)
