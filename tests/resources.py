
try:
    u = unicode
    string_types = (unicode, str)
except NameError:
    u = str
    string_types = (str,)