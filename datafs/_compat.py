
from contextlib import contextmanager
import os

try:
    u = unicode
    string_types = (unicode, str)
    from StringIO import StringIO

except NameError:
    u = str
    string_types = (str,)
    from io import StringIO


@contextmanager
def open_filelike(filelike, mode='r'):

    if hasattr(filelike, 'read'):
        yield filelike

    else:
        with open(filelike, mode) as f:
            yield f

