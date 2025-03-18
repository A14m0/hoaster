import flask
from flask import make_response, request, send_file
from loguru import logger as l
import os

# init app
app = flask.Flask(__name__)


@app.route('/<path:path>', methods=["GET", "PUT", "POST"])
def handle_route(path):
    path = f"/{path}"
    l.debug(f"Handling request to {path}")
    method_type = request.method.lower()
    # iterate through the provided routes until we find one...

    try:
        # iterate through the available payloads
        for r in app.config["ROUTES"][method_type]:
            # handle URL parameters
            items = []
            for k,_v in request.args.items():
                items.append(k)

            # match the route
            if path == r['route'] and items == r['params']:
                # found it, make sure we should really send a file
                if r['file'] == "":
                    # its not important
                    return make_response("Success.", r['code'])

                # pass it the file
                if os.path.isfile(r['file']):
                    l.debug("Found route")
                    return send_file(r['file'], as_attachment=True)
                else:
                    # the file in the config file doesn't exist...
                    l.warning(f"Failed to find file from config: {r['file']}")
                    return make_response(f"File '{r['file']}' not found.", 404)

    # something happened...
    except Exception as e:
        l.error(f"Failed to handle request: {e}")
        return make_response(f"Error handling request: {e}", 500)

    # if we make it down here, we didn't find an available route in the config
    #
    # could this technically lead to some kind of injection attack?
    # maybe :)      but i dont care
    l.warning(f"Failed to handle route: {path}")
    return make_response(f"Route '{path}' not found", 404)



def rest_server_main(config):
    l.info("Starting static main...")

    # store the page
    app.config["ROUTES"] = config

    l.debug(app.config["ROUTES"])

    # run the program
    app.run(debug=True, host="0.0.0.0")
