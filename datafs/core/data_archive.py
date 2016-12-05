from __future__ import absolute_import

from datafs.core.data_file import DataFile, LocalFile


class DataArchive(object):

    def __init__(self, api, archive_name, authority, service_path):
        self.api = api
        self.archive_name = archive_name

        self._authority_name = authority
        self._service_path = service_path

    @property
    def authority_name(self):
        return self._authority_name

    @property
    def authority(self):
        return self.api._authorities[self.authority_name]

    @property
    def service_path(self):
        return self._service_path

    @property
    def metadata(self):
        return self.api.manager.get_metadata(self.archive_name)

    @property
    def latest_hash(self):
        pass

    def update(self, filepath, cache=False, **kwargs):
        '''
        Enter a new version to a DataArchive

        Parameters
        ----------

        filepath : str
            The path to the file on your local file system

        cache : bool
            Save file to cache before upload (default False)

        **kwargs stored as update to metadata.


        .. todo::

            implement a way to prevent multiple uploads of the same file
        '''

        # Get hash value for file

        algorithm, hashval = self.api.hash_file(filepath)

        if hashval == self.latest_hash:
            self.update_metadata(kwargs)
            return

        checksum = {"algorithm": algorithm, "value": hashval}

        self.authority.upload(filepath, self.service_path)

        if cache and self.api.cache:
            self.api.cache.upload(filepath, self.service_path)

        # update records in self.api.manager
        self.api.manager.update(
            archive_name=self.archive_name,
            checksum=checksum,
            metadata=kwargs)

    def update_metadata(self, **kwargs):

        # just update records in self.api.manager

        self.api.manager.update(self.archive_name, kwargs)

    # File I/O methods

    @property
    def open(self):
        '''
        Opens a file for read/write
        '''

        return lambda *args, **kwargs: DataFile(self, *args, **kwargs)

    @property
    def get_sys_path(self):
        '''
        Returns a local path for read/write
        '''

        return lambda *args, **kwargs: LocalFile(self, *args, **kwargs)

    def isfile(self, *args, **kwargs):
        '''
        Check whether the path exists and is a file
        '''
        self.fs.isfile(self.path, *args, **kwargs)

    def getinfo(self, *args, **kwargs):
        '''
        Return information about the path e.g. size, mtime
        '''
        self.fs.getinfo(self.path, *args, **kwargs)

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

    def getmeta(self, *args, **kwargs):
        '''
        Get the value of a filesystem meta value, if it exists
        '''

        self.fs.getmeta(self.path, *args, **kwargs)

    def hasmeta(self, *args, **kwargs):
        '''
        Check if a filesystem meta value exists
        '''

        self.fs.hasmeta(self.path, *args, **kwargs)
