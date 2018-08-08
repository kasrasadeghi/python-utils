import sys
from contextlib import contextmanager
from pprint import pformat

import yaml


def zip_strcat(a, b) -> str:
    """
    strcats `a` and `b` horizontally, so `a` is on the left and `b` is on the right.
    requires that the str(b) >= str(a) in terms of the number of lines
    """
    a_lines = str(a).splitlines()
    a_llen  = max(map(len, a_lines)) # llen = line length
    b_lines = str(b).splitlines()
    b_llen  = max(map(len, b_lines))

    # precondition: len(b_lines) >= len(a_lines)
    a_lines += [""] * (len(b_lines) - len(a_lines))

    # left justification
    a_lines = [f"%-{a_llen+1}s | " % (x,) for x in a_lines]
    b_lines = [f"%-{b_llen+1}s" % (x,) for x in b_lines]

    combined_lines = map(lambda p: p[0] + p[1], zip(a_lines, b_lines))
    return "\n".join(combined_lines)


# data assertion library
def data_must_contain(*keys: str):
    def data_decorator(f):
        def g(data, *args, **kwargs):
            for key in keys:
                assert key in data, f"Error: expecting {key} in data argument for {f.__name__}"
            return f(data, *args, **kwargs)
        return g
    return data_decorator


### logging library


def indent(data: dict):
    data['indent_level'] += 1


def dedent(data: dict):
    data['indent_level'] -= 1


@contextmanager
def indent_context(data, message=None, end='\n'):
    if message:
        log(data, message, end=end)
    indent(data)
    yield
    dedent(data)


# can only be used by functions that take in a single argument config
def indent_decorator(message=None):
    def inner_decorator(f):
        def g(config):
            if message:
                log(config, message)
            with indent_context(config):
                return f(config)
        return g
    return inner_decorator


@data_must_contain('logs')
def log(data: dict, message: str, end='\n'):
    if 'indent_level' not in data:
        data['indent_level'] = 0

    indentation = data['indent_level']*'  '

    if '.' != message:
        message = message.replace('\n', '\n' + indentation)
        message = indentation + message + end

    data['logs'].append(message)
    print(message, end='')
    sys.stdout.flush()


# pretty log
def plog(data, obj, end='\n'):
    log(data, pformat(obj), end)

def flush_log(data) -> str:
    return "".join(data['logs'])


#### dictionary projection library

# without, antiproject, show a dictionary without certain keys
def without(d: dict, *keys: str):
    return {k:v for k,v in d.items() if k not in keys}
