""" poll.py contains poll(), a function for handling polling requests """

import time
from .util import indent_context, log

# the poll function
# takes:
#   @param data, the data dictionary
#   @param working, response -> bool
#     - a function from response to bool
#     - a response predicate
#     checks whether the request is finished by reading a response
#   @param query,
#     - a function from data to response
#     - a function that queries the server using the data for a new response
def poll(data, working, query):
    """
    @param data: the data dictionary
    @param working: response -> bool
    @param query: data -> response
    """
    before = time.time()
    resp = query(data)

    with indent_context(data, 'waiting for completion', end=''):
        while True:
            # query the resource
            resp = query(data)

            # if it's still working on it, log a dot, otherwise, break loop
            if working(resp):
                log(data, ".")
            else:
                break

            # if this is taking too long, timeout
            if time.time() - before > 5 * 60:  # 5 minutes
                log(data, "")
                log(data, str(resp))
                raise TimeoutError('Query did not finish in 5 minutes.')

            # otherwise, wait, then try again
            time.sleep(5)

        # the query is done, so log how long it took and return
        log(data, "")

        elapsed = time.time() - before
        log(data, f"{elapsed:.3}s")

    return resp
