
from contextlib import contextmanager

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


_module_contents = [u, string_types, StringIO, open_filelike]

__all__ = list(map(lambda x: x.__name__, _module_contents))
