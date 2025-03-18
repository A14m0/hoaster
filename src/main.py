import argparse
import json
from loguru import logger as l
import os


# local imports
from kafka_runner import kafka_main
from rest_client import rest_client_main
from rest_server import rest_server_main
from transmit import transmit_main

# The supported modes and their main functions.
# Functions have the signature:
#   `def func(config: JSON)`
MODES = {
    'kafka':        kafka_main,
    'rest_client':  rest_client_main,
    'rest_server':  rest_server_main,
    'transmit':     transmit_main,
}


if __name__ == "__main__":

    # build arg parser, and then parse
    prog = argparse.ArgumentParser(
        prog="Hoaster",
        description="A simple Python program to host dummy endpoints to test stuff against"
    )
    prog.add_argument("mode", help=f"The mode to execute with. Options include {MODES.keys()}")
    prog.add_argument("config", help="The JSON file containing all the different routes that are needed")
    args = prog.parse_args()

    # try to read the file
    if not os.path.exists(args.config):
        l.error(f"Path '{args.config}' doesn't exist!")
        exit(1)

    # now that we have the file, parse it
    with open(args.config) as f:
        dat = json.load(f)

    l.info(f"Loaded {len(dat)} routes")

    if args.mode not in MODES.keys():
        l.error(f"Unsupported mode '{args.mode}'. Valid options include {MODES.keys()}")
        exit(1)

    # run the target main function
    MODES[args.mode](dat)
