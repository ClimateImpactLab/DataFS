
import logging
import os

import fs.utils
from fs.opener import opener
from fs.osfs import OSFS

class DataArchive(object):
    def __init__(self, api, archive_name):
       self.api = api
       self.archive_name = archive_name


    @property
    def latest(self):
        raise NotImplementedError

    @latest.setter
    def latest(self, value):
        raise AttributeError('latest attribute cannot be set')


    @property
    def version_ids(self):
        '''
        Version ID history for an archive
        '''

        return self.api.manager.get_all_version_ids(self.archve_name)


    @version_ids.setter
    def version_ids(self, value):
        raise AttributeError('version_ids attribute cannot be set')


    @property
    def versions(self):
        '''
        File history for an archive
        '''
        return [self.get_version(v) for v in self.version_ids]

    @versions.setter
    def versions(self, value):
        raise AttributeError('versions attribute cannot be set')

    
    @property
    def metadata(self):
        return self.api.manager.get_metadata(self.archive_name)


    def get_version(self, version_id):
        '''
        Returns a DataFile for a specified version_id

        Parameters
        ----------
        version_id : str

        Returns
        -------
        version : object
            :py:class:`~datafs.core.DataFile` object

        '''

        self.api.manager.get_version(self.archive_name, version_id)


    def update(self, file, **kwargs):
        '''
        Enter a new version to a DataArchive

        Parameters
        ----------

        file : str
            The path to the file on your local file system



        '''

        # loop through upload services
        #   and put file to each

        version_id = self.api.create_version_id(self.archive_name, file)

        file_fs = OSFS(fs.path.dirname(os.path.abspath(file)))
        file_path = fs.path.basename(file)

        services = {}

        for service_name in self.api.upload_services:
            
            service = self.api.services[service_name]
            
            res = service.upload(file, self.archive_name, version_id)
            services[service_name] = res

        # also update records in self.api.manager
        self.api.manager.update(self.archive_name, version_id, services)


    def update_metadata(self, **kwargs):
        
        # just update records in self.api.manager
        
        self.api.manager.update(self.archive_name, **kwargs)
