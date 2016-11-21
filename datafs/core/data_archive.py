

class DataArchive(object):
    def __init__(self, api, archive_name):
       self.api = api
       self.archive_name = archive_name


    @property
    def latest(self):
        return self.get_version(sorted(self.version_ids)[-1])

    @latest.setter
    def latest(self, value):
        raise AttributeError('latest attribute cannot be set')


    @property
    def version_ids(self):
        '''
        Version ID history for an archive
        '''

        return self.api.manager.get_all_version_ids(self.archive_name)


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

        return self.api.manager.get_version(self.archive_name, version_id)


    def update(self, filepath, **kwargs):
        '''
        Enter a new version to a DataArchive

        Parameters
        ----------

        filepath : str
            The path to the file on your local file system


        .. todo::

            implement a way to prevent multiple uploads of the same file
        '''

        # Get hash value for file

        algorithm, hashval = self.api.hash_file(filepath)
        hashsummary = {"algorithm": algorithm, "value": hashval}


        # TODO: check for archive/version/hashval with manager
        #       Not sure what the best way to implement this is
        # services_with_hashval = self.api.manager.search_by_hashval() ??


        # loop through upload services
        #   and put file to each

        version_id = self.api.create_version_id(self.archive_name, filepath)

        services = []

        service_path = self.api.create_service_path(filepath, self.archive_name, version_id)

        for service_name in self.api.upload_services:
            
            service = self.api.services[service_name]
            
            service.upload(filepath, service_path)
            services.append(service_name)

        # update records in self.api.manager
        self.api.manager.update(
            archive_name = self.archive_name, 
            version_id = version_id, 
            service_path = service_path,
            service_data = services, 
            checksum = hashsummary)


    def update_metadata(self, **kwargs):
        
        # just update records in self.api.manager
        
        self.api.manager.update(self.archive_name, **kwargs)
