
import logging

class DataArchive(object):
	def __init__(self, api, achive_name):
       self.api = api
       self.achive_name = achive_name


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

        return self.api._manager.get_all_version_ids(self.archve_name)


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

        self.api._manager.get_version(self.archive_name, version_id)


    def update(self, file, **kwargs):

        # loop through upload services
        #   and put file
        
        # also update records in self.api._manager
        
        self.api._manager.update(self.archive_name, file, **kwargs)


    def update_metadata(self, **kwargs):
        
        # just update records in self.api._manager
        
        self.api._manager.update(self.archive_name, **kwargs)
