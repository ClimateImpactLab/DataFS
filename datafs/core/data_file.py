

class DataFile(object):
    '''
    Base class for DataFile objects

    '''


    def __init__(self, api, archive, version_id, fs, path):
        self.api = api
        self.archive = archive
        self.version_id = version_id
        self.fs = fs
        self.path = path

    @property
    def metadata(self):
        return self.archive.metadata

    @metadata.setter
    def metadata(self, value):
        raise AttributeError('metadata attribute cannot be set')

    def open(self, *args, **kwargs):
        '''
        Opens a file for read/writing
        '''

        return self.fs.open(self.path, *args, **kwargs)


    def isfile(self, *args, **kwargs):
        '''
        Check whether the path exists and is a file
        '''
        self.fs.isfile(self.path, *args, **kwargs)


    def remove(self, *args, **kwargs):
        '''
        Remove an existing file
        '''
        self.fs.remove(self.path, *args, **kwargs)


    def rename(self, *args, **kwargs):
        '''
        Atomically rename a file or directory
        '''
        self.fs.rename(self.path, *args, **kwargs)


    def getinfo(self, *args, **kwargs):
        '''
        Return information about the path e.g. size, mtime
        '''
        self.fs.getinfo(self.path, *args, **kwargs)


    def copy(self, *args, **kwargs):
        '''
        Copy a file to a new location
        '''

        self.fs.copy(self.path, *args, **kwargs)


    def desc(self, *args, **kwargs):
        '''
        Return a short descriptive text regarding a path
        '''

        self.fs.desc(self.path, *args, **kwargs)


    def exists(self, *args, **kwargs):
        '''
        Check whether a path exists as file or directory
        '''

        self.fs.exists(self.path, *args, **kwargs)


    def getpathurl(self, *args, **kwargs):
        '''
        Get an external URL at which the given file can be accessed, if possible
        '''

        self.fs.getpathurl(self.path, *args, **kwargs)


    def getsyspath(self, *args, **kwargs):
        '''
        Get a file's name in the local filesystem, if possible
        '''

        self.fs.getsyspath(self.path, *args, **kwargs)


    def getmeta(self, *args, **kwargs):
        '''
        Get the value of a filesystem meta value, if it exists
        '''

        self.fs.getmeta(self.path, *args, **kwargs)


    def getmmap(self, *args, **kwargs):
        '''
        Gets an mmap object for the given resource, if supported
        '''

        self.fs.getmmap(self.path, *args, **kwargs)


    def hassyspath(self, *args, **kwargs):
        '''
        Check if a path maps to a system path (recognized by the OS)
        '''

        self.fs.hassyspath(self.path, *args, **kwargs)


    def haspathurl(self, *args, **kwargs):
        '''
        Check if a path maps to an external URL
        '''

        self.fs.haspathurl(self.path, *args, **kwargs)


    def hasmeta(self, *args, **kwargs):
        '''
        Check if a filesystem meta value exists
        '''

        self.fs.hasmeta(self.path, *args, **kwargs)


    def move(self, *args, **kwargs):
        '''
        Move a file to a new location
        '''

        self.fs.move(self.path, *args, **kwargs)


    def settimes(self, *args, **kwargs):
        '''
        Sets the accessed and modified times of a path
        '''

        self.fs.settimes(self.path, *args, **kwargs)




