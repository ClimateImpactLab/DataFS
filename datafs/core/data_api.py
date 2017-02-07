from __future__ import absolute_import

from datafs.services.service import DataService
from datafs.core.data_archive import DataArchive
from datafs._compat import open_filelike


import fs.path

import hashlib
import fnmatch
import re

try:
    PermissionError
except NameError:
    class PermissionError(NameError):
        pass


class DataAPI(object):

    DefaultAuthorityName = None

    _ArchiveConstructor = DataArchive

    def __init__(self, default_versions=None, **kwargs):

        if default_versions is None:
            default_versions = {}

        self.user_config = kwargs

        self._manager = None
        self._cache = None
        self._authorities = {}

        self._default_versions = default_versions

        self._authorities_locked = False
        self._manager_locked = False

    def attach_authority(self, service_name, service):

        if self._authorities_locked:
            raise PermissionError('Authorities locked')

        self._authorities[service_name] = DataService(service)

    def lock_authorities(self):
        self._authorities_locked = True

    def lock_manager(self):
        self._manager_locked = True

    def attach_cache(self, service):

        if service in self._authorities.values():
            raise ValueError('Cannot attach an authority as a cache')
        else:
            self._cache = DataService(service)

    @property
    def manager(self):
        return self._manager
    # set cache attr

    @property
    def cache(self):
        return self._cache
    # get the default athority setting

    @property
    def default_authority_name(self):

        if self.DefaultAuthorityName is not None:
            return self.DefaultAuthorityName

        if len(self._authorities) == 0:
            raise ValueError(
                'No authorities found. See attach_authority.')

        if len(self._authorities) > 1:
            raise ValueError(
                'Authority ambiguous. Set authority or DefaultAuthorityName.')
        # get the zeroth key
        return list(self._authorities.keys())[0]

    # Do we want to provide a method for setting authorities
    @property
    def default_authority(self):
        return self._authorities[self.default_authority_name]
    # attach a metadata index

    def attach_manager(self, manager):

        if self._manager_locked:
            raise PermissionError('Manager locked')

        self._manager = manager

    def create(
            self,
            archive_name,
            authority_name=None,
            archive_path=None,
            versioned=True,
            raise_on_err=True,
            metadata=None,
            tags=None,
            helper=False):
        '''
        Create a DataFS archive

        Parameters
        ----------

        archive_name : str
            Name of the archive

        authority_name : str
            Name of the data service to use as the archive's data authority

        archive_path : str
            Path to use on the data services (optional)

        versioned : bool
            If true, store all versions with explicit version numbers (defualt)

        raise_on_err : bool
            Raise an error if the archive already exists (default True)

        metadata : dict
            Dictionary of additional archive metadata

        helper : bool
            If true, interactively prompt for required metadata (default False)


        '''

        if authority_name is None:
            authority_name = self.default_authority_name

        if authority_name not in self._authorities:
            raise KeyError('Authority "{}" not found'.format(authority_name))

        if archive_path is None:
            archive_path = self.create_archive_path(archive_name)

        if metadata is None:
            metadata = {}

        res = self.manager.create_archive(
            archive_name,
            authority_name,
            archive_path=archive_path,
            versioned=versioned,
            raise_on_err=raise_on_err,
            metadata=metadata,
            user_config=self.user_config,
            tags=tags,
            helper=helper)

        return self._ArchiveConstructor(
            api=self,
            **res)

    def get_archive(self, archive_name, default_version=None):

        res = self.manager.get_archive(archive_name)

        default_version = self._default_versions.get(archive_name, None)

        return self._ArchiveConstructor(
            api=self,
            default_version=default_version,
            **res)

    def filter(self, pattern=None, engine='path', prefix=None):
        '''

        Performs a filtered search on entire universe of archives
        according to pattern or prefix.

        Parameters
        ----------
        prefix: str
            string matching beginning characters of the archive or set of
            archives you are filtering

        pattern: str
            string matching the characters within the archive or set of
            archives you are filtering on

        engine: str
            string of value 'str', 'path', or 'regex'. That indicates the
            type of pattern you are filtering on


        Returns
        -------
        generator



        '''

        archives = self.manager.search(tuple([]), begins_with=prefix)

        if not pattern:
            for archive in archives:
                yield archive

        if engine == 'str':
            for arch in archives:
                if pattern in arch:
                    yield arch

        elif engine == 'path':
            # Change to generator version of fnmatch.filter

            for arch in archives:
                if fnmatch.fnmatch(arch, pattern):
                    yield arch

        elif engine == 'regex':
            for arch in archives:
                if re.search(pattern, arch):
                    yield arch

        else:
            raise ValueError(
                'search engine "{}" not recognized. '.format(engine) +
                'choose "str", "fn", or "regex"')

    def search(self, *query, **kwargs):
        '''
        Searches based on tags specified by users



        Parameters
        ---------
        query: str
            tags to search on. If multiple terms, provided in comma delimited
            string format

        prefix : str
            start of archive name. Providing a start string improves search
            speed.

        '''

        prefix = kwargs.get('prefix')

        return self.manager.search(query, begins_with=prefix)

    @classmethod
    def create_archive_path(cls, archive_name):
        '''
        Utility function for creating and checking internal service paths

        Parameters
        ----------

        archive_name : str
            Name of the archive from which to create a service path

        Returns
        -------

        archive_path : str
            Internal path used by services to reference archive data

        Default: split archive name on underscores

        Example
        -------

        .. code-block:: python

            >>> print(DataAPI.create_archive_path(
            ...     'pictures_2016_may_vegas_wedding.png'))
            pictures/2016/may/vegas/wedding.png

        *Overloading*

        Overload this function to change default internal service path format
        and to enforce certain requirements on paths:

        .. code-block:: python

            >>> class MyAPI(DataAPI):
            ...     @classmethod
            ...     def create_archive_path(cls, archive_name):
            ...         if '_' in archive_name:
            ...             raise ValueError('No underscores allowed!')
            ...         return archive_name
            ...
            >>> api = MyAPI
            >>> api.create_archive_path(
            ...   'pictures_2016_may_vegas_wedding.png')   # doctest: +ELLIPSIS
            Traceback (most recent call last):
            ...
            ValueError: No underscores allowed!


        '''

        return fs.path.join(*tuple(archive_name.split('_')))

    def delete_archive(self, archive_name):
        '''
        Delete an archive

        Parameters
        ----------

        archive_name : str
            Name of the archive to delete

        '''

        archive = self.get_archive(archive_name)

        archive.delete()

    @staticmethod
    def hash_file(f):
        '''
        Utility function for hashing file contents

        Overload this function to change the file equality checking algorithm

        Parameters
        ----------

        f : file-like
            File-like object or file path from which to compute checksum value


        Returns
        -------
        checksum : dict
            dictionary with {'algorithm': 'md5', 'checksum': hexdigest}

        '''

        md5 = hashlib.md5()

        with open_filelike(f, 'rb') as f_obj:
            for chunk in iter(lambda: f_obj.read(128 * md5.block_size), b''):
                md5.update(chunk)

        return {'algorithm': 'md5', 'checksum': md5.hexdigest()}

    def close(self):
        for service in self._authorities:
            self._authorities[service].fs.close()

        if self.cache:
            self.cache.fs.close()
