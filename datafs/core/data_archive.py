from __future__ import absolute_import

from datafs.core import data_file
from datafs.core.versions import BumpableVersion
from contextlib import contextmanager
import fs.utils
from fs.osfs import OSFS
import os


class DataArchive(object):

    def __init__(self, api, archive_name, authority_name, archive_path, versioned=True):
        self.api = api
        self.archive_name = archive_name

        self._authority_name = authority_name
        self._archive_path = archive_path

        self._versioned = versioned

    def __repr__(self):
        return "<{} {}://{}>".format(self.__class__.__name__,
                                     self.authority_name, self.archive_name)

    @property
    def versioned(self):
        return self._versioned

    
    def get_latest_version(self):

        versions = self.get_versions()
    
        if len(versions) == 0:
            return None
    
        else:
            return max(versions)

    
    def get_versions(self):

        if not self.versioned:
            return [None]

        versions = self.history
    
        if len(versions) == 0:
            return []
    
        else:
            return sorted(map(BumpableVersion, set([v['version'] for v in versions])))


    def get_version_path(self, version=None):
        '''
        Returns a storage path for the archive and version

        If the archive is versioned, the version number is used as the file path 
        and the archive path is the directory. If not, the archive path is used 
        as the file path.

        Parameters
        ----------
        version : str or object
            Version number to use as file name on versioned archives (default 
            latest)

        Examples
        --------

        .. code-block:: python

            >>> arch = DataArchive(None, 'arch', None, 'arch1', versioned=False)
            >>> print(arch.get_version_path())
            arch1
            >>>
            >>> ver = DataArchive(None, 'ver', None, 'arch2', versioned=True)
            >>> print(ver.get_version_path('0.0.0'))
            arch2/0.0.0
            >>>
            >>> print(ver.get_version_path('0.0.1a1'))
            arch2/0.0.1a1
            >>> 
            >>> print(ver.get_version_path('0.0.0'))
            arch2/0.0.0


        '''

        if self.versioned:
            if version is None:
                version = self.get_latest_version()

            if version is None:
                return fs.path.join(self.archive_path, str(BumpableVersion()))

            else:
                return fs.path.join(self.archive_path, str(version))

        else:
            return self.archive_path

    @property
    def authority_name(self):
        return self._authority_name

    @property
    def authority(self):
        return self.api._authorities[self.authority_name]

    @property
    def archive_path(self):
        return self._archive_path

    @property
    def metadata(self):
        return self.api.manager.get_metadata(self.archive_name)

    @property
    def latest_hash(self):
        return self.api.manager.get_latest_hash(self.archive_name)

    def get_version_hash(self, version=None):
        if self.versioned:
            if version is None:
                version = self.get_latest_version()

            if version is None:
                return None

            for ver in self.history:
                if BumpableVersion(ver['version']) == version:
                    return ver['checksum']

            raise ValueError('Version "{}" not found in archive history'.format(
                version))

        else:
            return self.latest_hash


    @property
    def history(self):
        return self.api.manager.get_version_history(self.archive_name)

    def update(
        self, 
        filepath, 
        cache=False, 
        remove=False, 
        bumpversion='patch', 
        prerelease=None, 
        dependencies=None,
        **kwargs):
        '''
        Enter a new version to a DataArchive

        Parameters
        ----------

        filepath : str
            The path to the file on your local file system

        cache : bool
            Turn on caching for this archive if not already on before update

        remove : bool
            removes a file from your local directory

        bumpversion : str
            Version component to update on write if archive is versioned. Valid 
            bumpversion values are 'major', 'minor', and 'patch', representing 
            the three components of the strict version numbering system (e.g. 
            "1.2.3"). If bumpversion is None the version number is not updated 
            on write. Either bumpversion or prerelease (or both) must be a 
            non-None value. If the archive is not versioned, bumpversion is 
            ignored.

        prerelease : str
            Prerelease component of archive version to update on write if 
            archive is versioned. Valid prerelease values are 'alpha' and 
            'beta'. Either bumpversion or prerelease (or both) must be a 
            non-None value. If the archive is not versioned, prerelease is 
            ignored.

        kwargs stored as update to metadata.


        '''

        latest_version = self.get_latest_version()

        hashval = self.api.hash_file(filepath)

        checksum = hashval['checksum']
        algorithm = hashval['algorithm']

        if checksum == self.latest_hash:
            self.update_metadata(kwargs)

            if remove and os.path.isfile(filepath):
                os.remove(filepath)

            return

        if self.versioned:
            if latest_version is None:
                latest_version = BumpableVersion()

            next_version = latest_version.bump(
                    kind = bumpversion, 
                    prerelease = prerelease,
                    inplace=False)

        else:
            next_version = None

        next_path = self.get_version_path(next_version)
        
        if cache:
            self.cache(next_version)

        if self.is_cached(next_version):
            self.authority.upload(filepath, next_path)
            self.api.cache.upload(filepath, next_path, remove=remove)

        else:
            self.authority.upload(filepath, next_path, remove=remove)

        self._update_manager(
            archive_metadata=kwargs, 
            version_metadata=dict(checksum=checksum, algorithm=algorithm, version=next_version, dependencies=dependencies))


    def _update_manager(self, archive_metadata={}, version_metadata={}):
        
        version_metadata['user_config'] = self.api.user_config


        # update records in self.api.manager
        self.api.manager.update(self.archive_name, version_metadata)
        self.update_metadata(archive_metadata)

    def update_metadata(self, metadata):

        # just update records in self.api.manager

        self.api.manager.update_metadata(self.archive_name, metadata)

    # File I/O methods

    @contextmanager
    def open(self, mode='r', version=None, bumpversion='patch', prerelease=None, dependencies = None, *args, **kwargs):
        '''
        Opens a file for read/write

        Parameters
        ----------
        mode : str
            Specifies the mode in which the file is opened (default 'r')

        version : str
            Version number of the file to open (default latest)

        bumpversion : str
            Version component to update on write if archive is versioned. Valid 
            bumpversion values are 'major', 'minor', and 'patch', representing 
            the three components of the strict version numbering system (e.g. 
            "1.2.3"). If bumpversion is None the version number is not updated 
            on write. Either bumpversion or prerelease (or both) must be a 
            non-None value. If the archive is not versioned, bumpversion is 
            ignored.

        prerelease : str
            Prerelease component of archive version to update on write if 
            archive is versioned. Valid prerelease values are 'alpha' and 
            'beta'. Either bumpversion or prerelease (or both) must be a 
            non-None value. If the archive is not versioned, prerelease is 
            ignored.


        args, kwargs sent to file system opener
        
        '''
        if version is None:
            latest_version = self.get_latest_version()
            version = latest_version

        else:
            latest_version = self.get_latest_version()

        version_hash = self.get_version_hash(version)

        if self.versioned:

            if latest_version is None:
                latest_version = BumpableVersion()

            next_version = latest_version.bump(
                kind = bumpversion, 
                prerelease = prerelease, 
                inplace = False)

            msg = "Version must be bumped on write. " \
                "Provide bumpversion and/or prerelease."

            assert next_version > latest_version, msg

            read_path = self.get_version_path(version)
            write_path = self.get_version_path(next_version)
        
        else:
            read_path = self.archive_path
            write_path = self.archive_path
            next_version = None

        # version_check returns true if fp's hash is current as of read
        version_check = lambda chk: chk['checksum'] == version_hash

        # Updater updates the manager with the latest version number
        updater = lambda **kwargs: self._update_manager(
            version_metadata=dict(version=next_version, dependencies=dependencies, **kwargs))

        opener = data_file.open_file(
            self.authority,
            self.api.cache,
            updater,
            version_check,
            self.api.hash_file,
            read_path, 
            write_path, 
            mode=mode,
            *args,
            **kwargs)

        with opener as f:
            yield f

    @contextmanager
    def get_local_path(self, version=None, bumpversion='patch', prerelease=None, dependencies=None, *args, **kwargs):
        '''
        Returns a local path for read/write

        Parameters
        ----------
        version : str
            Version number of the file to retrieve (default latest)

        bumpversion : str
            Version component to update on write if archive is versioned. Valid 
            bumpversion values are 'major', 'minor', and 'patch', representing 
            the three components of the strict version numbering system (e.g. 
            "1.2.3"). If bumpversion is None the version number is not updated 
            on write. Either bumpversion or prerelease (or both) must be a 
            non-None value. If the archive is not versioned, bumpversion is 
            ignored.

        prerelease : str
            Prerelease component of archive version to update on write if 
            archive is versioned. Valid prerelease values are 'alpha' and 
            'beta'. Either bumpversion or prerelease (or both) must be a 
            non-None value. If the archive is not versioned, prerelease is 
            ignored.

        '''
        if version is None:
            latest_version = self.get_latest_version()
            version = latest_version

        else:
            latest_version = self.get_latest_version()

        version_hash = self.get_version_hash(version)

        if self.versioned:

            if latest_version is None:
                latest_version = BumpableVersion()

            next_version = latest_version.bump(
                kind = bumpversion, 
                prerelease = prerelease, 
                inplace = False)

            msg = "Version must be bumped on write. " \
                "Provide bumpversion and/or prerelease."

            assert next_version > latest_version, msg

            read_path = self.get_version_path(version)
            write_path = self.get_version_path(next_version)
        
        else:
            read_path = self.archive_path
            write_path = self.archive_path
            next_version = None

        # version_check returns true if fp's hash is current as of read
        version_check = lambda chk: chk['checksum'] == version_hash

        # Updater updates the manager with the latest version number
        updater = lambda **kwargs: self._update_manager(
            version_metadata=dict(version=next_version, dependencies=dependencies, **kwargs))

        path = data_file.get_local_path(
            self.authority,
            self.api.cache,
            updater,
            version_check,
            self.api.hash_file,
            read_path,
            write_path)

        with path as fp:
            yield fp



    def download(self, filepath, version=None):
        '''
        Downloads a file from authority to local path
        1. First checks in cache to check if file is there and if it is, is it up to date
        2. If it is not up to date, it will download the file to cache
        3. If not break
        '''

        if version is None:
            version = self.get_latest_version()

        dirname, filename= os.path.split(
            os.path.abspath(os.path.expanduser(filepath)))

        assert os.path.isdir(dirname), 'Directory  not found: "{}"'.format(
            dirname)

        local = OSFS(dirname)

        version_hash = self.get_version_hash(version)

        # version_check returns true if fp's hash is current as of read
        version_check = lambda chk: chk['checksum'] == version_hash

        if os.path.exists(filepath):
            if version_check(self.api.hash_file(filepath)):
                return

        read_path = self.get_version_path(version)

        with data_file._choose_read_fs(
            self.authority, 
            self.api.cache, 
            read_path, 
            version_check, 
            self.api.hash_file) as read_fs:

            fs.utils.copyfile(
                read_fs,
                read_path,
                local,
                filename)

    def delete(self):
        '''
        Delete the archive

        .. warning::

            Deleting an archive will erase all data and metadata permanently.
            This functionality can be removed by subclassing and overloading
            this method. For help subclassing DataFS see
            :ref:`Subclassing DataFS <tutorial-subclassing>`

        '''

        for version in self.get_versions():
            if self.authority.fs.exists(self.get_version_path(version)):
                self.authority.fs.remove(self.get_version_path(version))

            if self.api.cache:
                if self.api.cache.fs.exists(self.get_version_path(version)):
                    self.api.cache.fs.remove(self.get_version_path(version))

        self.api.manager.delete_archive_record(self.archive_name)

    def isfile(self, version=None, *args, **kwargs):
        '''
        Check whether the path exists and is a file
        '''

        path = self.get_version_path(version)
        self.authority.fs.isfile(path, *args, **kwargs)


    def getinfo(self, version=None, *args, **kwargs):
        '''
        Return information about the path e.g. size, mtime
        '''

        path = self.get_version_path(version)
        self.authority.fs.getinfo(path, *args, **kwargs)


    def desc(self, version=None, *args, **kwargs):
        '''
        Return a short descriptive text regarding a path
        '''

        path = self.get_version_path(version)
        self.authority.fs.desc(path, *args, **kwargs)


    def exists(self, version=None, *args, **kwargs):
        '''
        Check whether a path exists as file or directory
        '''

        path = self.get_version_path(version)
        self.authority.fs.exists(path, *args, **kwargs)


    def getmeta(self, version=None, *args, **kwargs):
        '''
        Get the value of a filesystem meta value, if it exists
        '''

        path = self.get_version_path(version)
        self.authority.fs.getmeta(path, *args, **kwargs)


    def hasmeta(self, version=None, *args, **kwargs):
        '''
        Check if a filesystem meta value exists
        '''

        path = self.get_version_path(version)
        self.authority.fs.hasmeta(path, *args, **kwargs)


    def is_cached(self, version=None):
        '''
        Set the cache property to start/stop file caching for this archive
        '''

        if version is None:
            version = self.get_latest_version()

        if self.api.cache and self.api.cache.fs.isfile(self.get_version_path(version)):
            return True

        return False

    def cache(self, version=None):

        if not self.api.cache:
            raise ValueError('No cache attached')

        if version is None:
            version = self.get_latest_version()

        if not self.api.cache.fs.isfile(self.get_version_path(version)):
            data_file._touch(self.api.cache.fs, self.get_version_path(version))

        assert self.api.cache.fs.isfile(
            self.get_version_path(version)), "Cache creation failed"


    def remove_from_cache(self, version=None):

        if version is None:
            version = self.get_latest_version()

        if self.api.cache.fs.isfile(self.get_version_path(version)):
            self.api.cache.fs.remove(self.get_version_path(version))

    def get_dependencies(self, version=None):
        '''
        Parameters
        ----------
        version: str
            string representing version number whose dependencies you are looking up
        '''

        if version is None:
            raise ValueError('No version provided')

        for i,v in enumerate(self.history):
            if v['version'] == version:
                return self.history[i]['dependencies']


