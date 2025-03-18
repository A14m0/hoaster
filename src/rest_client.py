# Holds stuff to create a REST-style client for your service :)

from loguru import logger as l
import os
import requests
from time import sleep

def handle_file(param):
    """Handles adding a file to the request"""
    # make sure the path exists
    if not os.path.exists(param):
        l.critical(f"While handling file in request: '{param}' doesn't exist!")
        return None

    # prep the kwarg
    return {"files": {param: open(param, 'rb')}}





# define a lookup for method types
METHOD_LOOKUP = {
    'get':      requests.get,
    'put':      requests.put,
    'post':     requests.post,
    'delete':   requests.delete
}


# define a lookup for parameters
PARAMS_LOOKUP = {
    'file':     handle_file
}


def rest_client_main(config):
    """Handles creating a REST-style client"""

    # keep track of some state
    STATE = {
        'index': 0,
        'repeat': 0
    }
    URL = config["url"]

    # make sure the user is ready to receive
    input("""'Before I continue, are you connected and ready to receive messages?
As soon as you hit enter, I'm going to start running requests against whatever's in my config.
It's not my fault if you're not ready for them!'
    - Hoaster

    Press enter when ready...""")

    # now that we have the go-ahead, lets get it :)
    while STATE['index'] < len(config['requests']):
        v = config['requests'][STATE['index']]
        # first make a complete URI
        full_uri = f"{URL}{v['route']}"

        # deterine the kind of request we need to make
        if v['method'] not in METHOD_LOOKUP.keys():
            l.critical(f"Unknown method '{v['method']}'")
            return

        req = METHOD_LOOKUP[v['method']]

        # now that we know the request method, lets see if
        # there's parameters we need to set
        kwargs = {}
        for param, val in v['params'].items():
            if param not in PARAMS_LOOKUP.keys():
                l.critical(f"Unsupported parameter '{param}'")
                return

            kwargs |= PARAMS_LOOKUP[param](val)

        l.debug(f"Using kwargs: '{kwargs}'")

        # To the unfortunate soul reading this code, I ask you lo' and behold
        #
        # I am eternally hating on Python. "oh, its so slow", "stupid
        # dynamically typed languages", etc. However, this? This right below
        # here? *This* is fuckin incredible, how flexible Python can be when
        # you really just throw good programming practices out the window. It's
        # like C, but without the SEGV... Which must be worth something.
        #
        # Absolute fuckin wizardry
        try:
            req(full_uri, **kwargs)
        except Exception as e:
            l.critical(f"{v['method']} request to {full_uri} failed: '{e}'")
            return

        # now see how long we need to sleep for
        sleep(v['delay'])

        # update state
        if STATE['repeat'] >= v[STATE['index']]['repeat']:
            STATE['index'] += 1
            STATE['repeat'] = 0
        else:
            STATE['repeat'] += 1

        l.debug(f"Current state: {STATE}")

    l.warning(f"Hit end of available payloads in config (count: {len(config['produce'])}). Halting...")
