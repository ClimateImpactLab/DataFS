from __future__ import absolute_import

from datafs.services.service import DataService
from datafs.core.data_archive import DataArchive
from contextlib import contextmanager

import fs.path

import os
import time
import hashlib


try:
    PermissionError
except:
    class PermissionError(NameError):
        pass


def enforce_user_config_requirements(func):
    '''
    Method decorator for DataAPI enforcing user_config requirements
    '''

    def inner(self, *args, **kwargs):
        for kw in self.REQUIRED_USER_CONFIG.keys():
            if kw not in self.user_config:
                raise KeyError(
                    'Required API configuration item "{}" not found'.format(kw))

        return func(self, *args, **kwargs)
    return inner


class DataAPI(object):


    TimestampFormat = '%Y%m%d-%H%M%S'

    DefaultAuthorityName = None

    _ArchiveConstructor = DataArchive

    REQUIRED_USER_CONFIG = {
    }

    REQUIRED_ARCHIVE_METADATA = {
    }

    def __init__(self, **kwargs):

        self.user_config = kwargs

        self._manager = None
        self._cache = None
        self._authorities = {}

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
    #set cache attr
    @property
    def cache(self):
        return self._cache
    #get the default athority setting 
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
        #get the zeroth key
        return list(self._authorities.keys())[0]

    #Do we want to provide a method for setting authorities
    @property
    def default_authority(self):
        return self._authorities[self.default_authority_name]
    #attach a metadata index
    def attach_manager(self, manager):

        if self._manager_locked:
            raise PermissionError('Manager locked')

        self._manager = manager
        self.manager.api = self

    @enforce_user_config_requirements
    def create_archive(
            self,
            archive_name,
            authority_name=None,
            service_path=None,
            raise_on_err=True,
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

        raise_on_err : bool
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
            raise_on_err=raise_on_err,
            metadata=metadata)

    @enforce_user_config_requirements
    def get_archive(self, archive_name):

        return self.manager.get_archive(archive_name)

    @property
    @enforce_user_config_requirements
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

        @contextmanager
        def open_file(f):

            if hasattr(f, 'read'):
                yield f

            else:
                with open(f, 'rb') as f_obj:
                    yield f_obj

        md5 = hashlib.md5()

        with open_file(f) as f_obj:
            for chunk in iter(lambda: f_obj.read(128 * md5.block_size), b''):
                md5.update(chunk)

        return {'algorithm': 'md5', 'checksum': md5.hexdigest()}

    def close(self):
        for service in self._authorities:
            self._authorities[service].fs.close()

        if self.cache:
            self.cache.fs.close()