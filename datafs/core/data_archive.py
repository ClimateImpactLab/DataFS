from __future__ import absolute_import

from datafs.core import data_file
import fs.utils
from contextlib import contextmanager
    

class DataArchive(object):

    def __init__(self, api, archive_name, authority, service_path):
        self.api = api
        self.archive_name = archive_name

        self._authority_name = authority
        self._service_path = service_path

    def __repr__(self):
        return "<{} {}://{}>".format(self.__class__.__name__, self.authority_name, self.archive_name)

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

    def update(self, filepath, **kwargs):
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

        checksum = self.api.hash_file(filepath)

        if checksum['checksum'] == self.latest_hash:
            self.update_metadata(kwargs)
            return

        self.authority.upload(filepath, self.service_path)

        if self.cache:
            self.api.cache.upload(filepath, self.service_path)

        self._update_manager(checksum, kwargs)

    def _update_manager(self, checksum, metadata={}):

        # update records in self.api.manager
        self.api.manager.update(
            archive_name=self.archive_name,
            checksum=checksum,
            metadata=metadata)

    def update_metadata(self, metadata):

        # just update records in self.api.manager

        self.api.manager.update_metadata(self.archive_name, metadata)

    # File I/O methods

    @contextmanager
    def open(self, mode='r', *args, **kwargs):
        '''
        Opens a file for read/write
        '''

        latest_hash = self.latest_hash

        # version_check returns true if fp's hash is current as of read
        version_check = lambda chk: chk['checksum'] == latest_hash

        opener = data_file.open_file(
            self.authority, 
            self.api.cache, 
            self._update_manager, 
            self.service_path, 
            version_check,
            self.api.hash_file,
            mode,
            *args, 
            **kwargs)

        with opener as f:
            yield f


    @contextmanager
    def get_local_path(self):
        '''
        Returns a local path for read/write
        '''
        
        latest_hash = self.latest_hash

        # latest_version_check returns true if fp's hash is current as of read
        latest_version_check = lambda fp: self.api.hash_file(fp) == latest_hash

        path = data_file.get_local_path(
            self.authority, 
            self.api.cache, 
            self._update_manager, 
            self.service_path, 
            version_check,
            self.api.hash_file)

        with path as fp:
            yield fp


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

    @property
    def cache(self):
        '''
        Set the cache property to start/stop file caching for this archive
        '''
        
        if not self.api.cache:
            return False

        if self.api.cache.fs.isfile(self.service_path):
            return True

    @cache.setter
    def cache(self, value):

        if not self.api.cache:
            raise ValueError('No cache attached')

        if value:

            if not self.api.cache.fs.isfile(self.service_path):
                self.api.cache.fs.makedir(
                    fs.path.dirname(self.service_path),
                    recursive=True,
                    allow_recreate=True)
                self.api.cache.fs.createfile(self.service_path)

            else:
                # cache exists
                pass

        else:

            if self.api.cache.fs.isfile(self.service_path):
                self.api.cache.fs.remove(self.service_path)
