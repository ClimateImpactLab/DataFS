
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

    elif os.path.isfile(filelike):
        with open(filelike, mode) as f:
            yield f

    elif isinstance(filelike, string_types):
        yield StringIO(filelike)

    else:
        raise ValueError('Cannot open "{}"'.format(filelike))