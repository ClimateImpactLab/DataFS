from __future__ import absolute_import

from datafs.services.service import DataService, CachingService
from datafs.core.data_archive import DataArchive

import fs.path

import os
import time
import hashlib


class DataAPI(object):

    TimestampFormat = '%Y%m%d-%H%M%S'

    DefaultAuthorityName = None

    _ArchiveConstructor = DataArchive

    def __init__(self, username, contact):
        self.username = username
        self.contact = contact

        self._manager = None
        self._cache = None
        self._authorities = {}

        self._authorities_locked = False
        self._manager_locked = False

    def attach_authority(self, service_name, service):

        if self._authorities_locked:
            raise ValueError('Authorities locked')

        self._authorities[service_name] = DataService(service)
        self._authorities[service_name].api = self

    def attach_cache(self, service):
        self._cache = CachingService(service)
        self._cache.api = self

    @property
    def manager(self):
        return self._manager

    @property
    def cache(self):
        return self._cache

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

        return list(self._authorities.keys())[0]

    @property
    def default_authority(self):
        return self._authorities[self.default_authority_name]

    def attach_manager(self, manager):

        if self._manager_locked:
            raise ValueError('Manager locked')

        self._manager = manager
        self.manager.api = self

    def create_archive(
            self,
            archive_name,
            authority_name=None,
            service_path=None,
            raise_if_exists=True,
            metadata={}):
        '''
        Create a DataFS archive

        Parameters
        ----------

        archive_name : str
            Name of the archive

        authority_name : str
            Name of the data service to use as the archive's version "authority"

        service_path : str
            Path to use on the data services (optional)

        raise_if_exists : bool
            Raise an error if the archive already exists (default True)

        **kwargs will be passed to the archive as metadata
            
    

        
        '''

        if authority_name is None:
            authority_name = self.default_authority_name

        if service_path is None:
            service_path = self.create_service_path(archive_name)

        return self.manager.create_archive(
            archive_name,
            authority_name,
            service_path=service_path,
            raise_if_exists=raise_if_exists,
            metadata=metadata)

    def get_archive(self, archive_name):
        return self.manager.get_archive(archive_name)

    @property
    def archives(self):
        return self.manager.get_archives()

    @classmethod
    def create_timestamp(cls):
        '''
        Utility function for formatting timestamps

        Overload this function to change timestamp formats
        '''

        return time.strftime(cls.TimestampFormat, time.gmtime())

    @classmethod
    def create_service_path(cls, archive_name):
        '''
        Utility function for creating and checking internal service paths

        Parameters
        ----------

        archive_name : str
            Name of the archive from which to create a service path

        Returns
        -------

        service_path : str
            Internal path used by services to reference archive data

        Default: split archive name on underscores

        Example
        -------

        .. code-block:: python

            >>> print(DataAPI.create_service_path(
            ...     'pictures_2016_may_vegas_wedding.png'))
            pictures/2016/may/vegas/wedding.png

        *Overloading*

        Overload this function to change default internal service path format
        and to enforce certain requirements on paths:

        .. code-block:: python

            >>> class MyAPI(DataAPI):
            ...     @classmethod
            ...     def create_service_path(cls, archive_name):
            ...         if '_' in archive_name:
            ...             raise ValueError('No underscores allowed!')
            ...         return archive_name
            ...
            >>> api = MyAPI
            >>> api.create_service_path(
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
    def hash_file(filepath):
        '''
        Utility function for hashing file contents

        Overload this function to change the file equality checking algorithm

        Parameters


        Returns
        -------
        algorithm : str
            Name/description of the algorithm being used.

        value : str
            Hash digest value
        '''


        if os.path.isfile(filepath):
            with open(filepath, 'rb') as f:
                hashval = hashlib.md5(f.read())


        return 'md5', hashval.hexdigest()

    

