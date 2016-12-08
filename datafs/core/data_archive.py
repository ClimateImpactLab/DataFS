from __future__ import absolute_import

from datafs.core.data_file import FileOpener, FilePathOpener

    

class DataArchive(object):

    def __init__(self, api, archive_name, authority, service_path):
        self.api = api
        self.archive_name = archive_name

        self._authority_name = authority
        self._service_path = service_path

    def __repr__(self):
        return "<{}, archive_name: '{}'>".format(self.__class__.__name__, self.archive_name)

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
        return self.api.manager.get_latest_hash(self.archive_name)

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

        checksum = {'algorithm': algorithm, 'checksum': hashval}

        self.authority.upload(filepath, self.service_path)

        if cache:
            self.cache()

        # update records in self.api.manager
        self.api.manager.update(
            archive_name=self.archive_name,
            checksum=checksum,
            metadata=kwargs)

    def update_metadata(self, metadata):

        # just update records in self.api.manager

        self.api.manager.update_metadata(self.archive_name, metadata)

    # File I/O methods

    @property
    def open(self):
        '''
        Opens a file for read/write
        '''

        return lambda *args, **kwargs: FileOpener(self, *args, **kwargs)

    @property
    def get_sys_path(self):
        '''
        Returns a local path for read/write
        '''

        return lambda *args, **kwargs: FilePathOpener(self, *args, **kwargs)

    def delete(self):
        '''
        Delete the archive

        .. warning::

            Deleting an archive will erase all data and metadata permanently.
            This functionality can be removed by subclassing and overloading 
            this method. For help subclassing DataFS see 
            :ref:`Subclassing DataFS <tutorial-subclassing>`
        
        '''

        if self.authority.fs.exists(self.archive_name):
            self.authority.fs.delete(self.archive_name)

        if self.api.cache:
            if self.api.cache.fs.exists(self.archive_name):
                self.api.cache.fs.delete(self.archive_name)

        self.api.manager.delete_archive_record(self.archive_name)


    def isfile(self, *args, **kwargs):
        '''
        Check whether the path exists and is a file
        '''
        self.authority.fs.isfile(self.path, *args, **kwargs)

    def getinfo(self, *args, **kwargs):
        '''
        Return information about the path e.g. size, mtime
        '''
        self.authority.fs.getinfo(self.path, *args, **kwargs)

    def desc(self, *args, **kwargs):
        '''
        Return a short descriptive text regarding a path
        '''

        self.authority.fs.desc(self.path, *args, **kwargs)

    def exists(self, *args, **kwargs):
        '''
        Check whether a path exists as file or directory
        '''

        self.authority.fs.exists(self.path, *args, **kwargs)

    def getmeta(self, *args, **kwargs):
        '''
        Get the value of a filesystem meta value, if it exists
        '''

        self.authority.fs.getmeta(self.path, *args, **kwargs)

    def hasmeta(self, *args, **kwargs):
        '''
        Check if a filesystem meta value exists
        '''

        self.authority.fs.hasmeta(self.path, *args, **kwargs)


    def cache(self, authority, service_path):
        
        if not self.api.cache:

            raise ValueError('No Cache attached')

        self.api.cache.upload(filepath, self.service_path)


