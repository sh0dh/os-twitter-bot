import sys
from pathlib import Path
from subprocess import CalledProcessError, check_call

from config.console import logger

PROJECT_ROOT = Path(__file__).parents[1]


def _call(cmd, options=[]) -> None:
    command = cmd.split(" ") + options
    logger.log(">>>>>>>>     {}".format(" ".join(command)))
    try:
        check_call(command)
    except CalledProcessError as ex:
        print(f"[FAIL]  {ex}")
        logger.log("<<<<<<<<<< ")
        sys.exit(2)
    logger.log("<<<<<<<<<< ")
