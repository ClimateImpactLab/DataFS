
class FileOpener(object):
    '''
    Handles the opening of a DataFS file object
    '''

    def __init__(self, fs, path):
        self._fs = fs
        self._path = path
        self._open_file_obj = None
    
    def open(self, *args, **kwargs):
        self._open_file_obj = self._fs.open(self._path, *args, **kwargs)
        return self._open_file_obj
    
    def close(self):
        self._open_file_obj.close()
