from __future__ import absolute_import

from datafs.managers.manager import BaseDataManager
from datafs.services.service import DataService

from fs.multifs import MultiFS
import fs.path

import time, hashlib

class DataAPI(object):

    DatabaseName = 'MyDatabase'
    DataTableName = 'DataFiles'

    TimestampFormat = '%Y%m%d-%H%M%S'

    def __init__(self, username, contact):
        self.username = username
        self.contact = contact

        self.manager = None
        self.authorities = {}
        self.cache = None

    def attach_authority(self, service_name, service):
        self.authorities[service_name] = DataService(service)
        self.authorities[service_name].api = self

    # @property
    # def download_service(self):
    #     _download_service = MultiFS()

    #     for service_name in reversed(list(self.download_priority)):
    #         _download_service.addfs(service_name, self.authorities[service_name].fs)

    #     return DataService(_download_service)

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

    @classmethod
    def create_timestamp(cls):
        '''
        Utility function for formatting timestamps

        Overload this function to change timestamp formats
        '''

        return time.strftime(cls.TimestampFormat, time.gmtime())

    @classmethod
    def create_service_path(cls, filepath, archive_name):
        '''
        Utility function for creating internal service paths

        Overload this function to change internal service path format
        '''

        return fs.path.join(*tuple(archive_name.split('.')))

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

