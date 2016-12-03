from __future__ import absolute_import

from datafs.managers.manager import BaseDataManager
from datafs.services.service import DataService

from fs.multifs import MultiFS
from collections import OrderedDict
import fs.path

import time, hashlib

class DataAPI(object):

    DatabaseName = 'MyDatabase'
    DataTableName = 'DataFiles'

    TimestampFormat = '%Y%m%d-%H%M%S'

    def __init__(self, username, contact, download_priority=None, upload_services=None):
        self.username = username
        self.contact = contact

        self.manager = None
        self.services = OrderedDict()

        self._download_priority = download_priority
        self._upload_services = upload_services

    @property
    def download_priority(self):
        if self._download_priority is None:
            return self.services.keys()
        else:
            return self._download_priority

    @download_priority.setter
    def download_priority(self, value):
        self._download_priority = value

    @property
    def upload_services(self):
        if self._upload_services is None:
            return self.services.keys()
        else:
            return self._upload_services

    @upload_services.setter
    def upload_services(self, value):
        self._upload_services = value

    def attach_service(self, service_name, service):
        self.services[service_name] = DataService(service)
        self.services[service_name].api = self

    @property
    def download_service(self):
        _download_service = MultiFS()

        for service_name in reversed(list(self.download_priority)):
            _download_service.addfs(service_name, self.services[service_name].fs)

        return DataService(_download_service)

    def attach_manager(self, manager):
        self.manager = manager
        self.manager.api = self

    def create_archive(self, archive_name, raise_if_exists=True, **metadata):
        self.manager.create_archive(archive_name, raise_if_exists=raise_if_exists, **metadata)

    def get_archive(self, archive_name):
        return self.manager.get_archive(archive_name)

    @property
    def archives(self):
        self.manager.get_archives()

    @archives.setter
    def archives(self):
        raise AttributeError('archives attribute cannot be set')

    @classmethod
    def create_timestamp(cls):
        '''
        Utility function for formatting timestamps

        Overload this function to change timestamp formats
        '''

        return time.strftime(cls.TimestampFormat, time.gmtime())

    @classmethod
    def create_version_id(cls, archive_name, filepath):
        '''
        Utility function for creating version IDs

        Overload this function to change version naming scheme
        '''

        return cls.create_timestamp()

    @classmethod
    def create_service_path(cls, filepath, archive_name, version_id):
        '''
        Utility function for creating internal service paths

        Overload this function to change internal service path format
        '''

        return fs.path.join(*tuple(archive_name.split('.') + [version_id + fs.path.splitext(filepath)[1]]))

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

        with open(filepath, 'rb') as f:
            hashval = hashlib.md5(f.read())

        return 'md5', hashval.hexdigest()

