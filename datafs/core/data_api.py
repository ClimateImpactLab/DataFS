from __future__ import absolute_import

from datafs.managers.manager import BaseDataManager
from datafs.services.service import DataService, CachingService

from fs.multifs import MultiFS
from collections import OrderedDict
import fs.path

import os
import time
import hashlib

class DataAPI(object):

    TimestampFormat = '%Y%m%d-%H%M%S'

    DefaultAuthorityName = None

    def __init__(self, username, contact):
        self.username = username
        self.contact = contact

        self._manager = None
        self._cache = None
        self._authorities = {}

    def attach_authority(self, service_name, service):
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
            raise ValueError('No authorities have been attached. Use DataApi.attach_authority to attach a data service.')

        if len(self._authorities) > 1:
            raise ValueError('Default authority ambiguous. Specify an authority or set the DefaultAuthorityName attribute.')

        return list(self._authorities.keys())[0]


    @property
    def default_authority(self):
        return self._authorities[self.default_authority_name]

    def attach_manager(self, manager):
        self._manager = manager
        self.manager.api = self

    def create_archive(self, archive_name, authority_name=None, service_path=None, raise_if_exists=True, **metadata):
        if authority_name is None:
            authority_name = self.default_authority_name

        if service_path is None:
            service_path = self.create_service_path(archive_name)

        self.manager.create_archive(archive_name, authority_name, service_path=service_path, raise_if_exists=raise_if_exists, **metadata)

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

            >>> print(DataAPI.create_service_path('pictures_2016_may_vegas_wedding.png'))
            pictures/2016/may/vegas/wedding.png

        Overloading
        -----------

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
            >>> api.create_service_path('pictures_2016_may_vegas_wedding.png')   # doctest: +ELLIPSIS
            Traceback (most recent call last):
            ...
            ValueError: No underscores allowed!


        '''

        return fs.path.join(*tuple(archive_name.split('_')))


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

