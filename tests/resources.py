
try:
    u = unicode
    string_types = (unicode, str)
except NameError:
    u = str
    string_types = (str,)


def upload(tfs, fp):
    fs.utils.copyfile(tfs, fp, a, fp)
