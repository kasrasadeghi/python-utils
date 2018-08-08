# flask_cors doesn't return readable exceptions

from functools import update_wrapper
from flask import make_response, request, Response
import traceback

# http://flask.pocoo.org/snippets/56/
def cross_origin(f):
    def wrapped_function(*args, **kwargs):
        if request.method == 'OPTIONS':
            resp = Response()
        else:
            try:
                resp = make_response(f(*args, **kwargs))
            except BaseException as e:
                resp = make_response(type(e).__name__ + ": " + str(e), 500)
                traceback.print_exc()
        if request.method not in {'OPTIONS', 'GET', 'POST'}:
            return resp

        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Boundary, Cache-Control, *'
        resp.headers['Access-Control-Max-Age'] = str(21600)
        resp.headers['Access-Control-Allow-Credentials'] = True
        return resp

    f.provide_automatic_options = False
    return update_wrapper(wrapped_function, f)
