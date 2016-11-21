
from __future__ import absolute_import
import time



class BaseDataManager(object):
    '''
    Base class for DataManager metadata store objects

    Should be subclassed. Not intended to be used directly.
    '''

    def __init__(self, api=None):
        self.api = api


    def update(self, archive_name, version_id, service_data, **metadata):
        '''
        Register a new version for archive ``archive_name``

        .. note ::
        
            need to implement hash checking to prevent duplicate writes

        '''

        version_data = metadata

        version_data["author"] = version_data.get("author", self.api.username)
        version_data["contact"] = version_data.get("contact", self.api.contact)
        version_data["updated"] = version_data.get("updated", self.api.create_timestamp())

        version_data["version_id"] = version_id
        version_data["services"] = service_data

        self._update(archive_name, version_id, version_data)

    def update_metadata(self, archive_name, **kwargs):
        '''
        Update metadata for archive ``archive_name``
        '''

        self._update_metadata(archive_name, **kwargs)

    def get_services_for_version(self, archive_name, version_id):
        '''
        Return services available for version ``version_id`` of archive ``archive_name``
        
        Returns
        -------
        services : list
            list of available service obejcts

        .. note ::

            this method does not check to make sure the version is available 
            with this service. This is the responsibility of the consumer of the 
            service list.

        '''

        self._get_services_for_version(archive_name, version_id)


    def get_datafile_from_service(self, archive_name, version_id, service):
        '''
        Return a DataFile object from a specific service
        '''

        return self._get_datafile_from_service(archive_name, version_id, service)


    def get_all_version_ids(self, archive_name):
        '''
        List version IDs available for ``archive_name``

        Returns
        -------
        version_ids : list

        '''

        return self._get_all_version_ids(archive_name)


    def get_version(self, archive_name, version_id):
        '''
        Retrieve a DataFile for the specified version from available services

        Parameters
        ----------
        archive_name : str
            name of the archive

        version_id : str
            data version to retrieve from services

        Returns
        -------
        version : object
            DataFile object corresponding to version ``version_id``

        '''

        service_path = self._get_service_path(archive_name, version_id)
        return self.api.download_service.get_datafile(archive_name, version_id, service_path)


    def create_archive(self, archive_name, raise_if_exists=True, **metadata):
        '''
        Create a new data archive

        Returns
        -------
        archive : object
            new :py:class:`~datafs.core.data_archive.DataArchive` object

        '''

        metadata['creator'] = metadata.get('creator', self.api.username)
        metadata['contact'] = metadata.get('contact', self.api.contact)
        metadata['creation_date'] = metadata.get('creation_date', self.api.create_timestamp())

        if raise_if_exists:
            self._create_archive(archive_name, **metadata)
        else:
            self._create_if_not_exists(archive_name, **metadata)


    def get_archive(self, archive_name):
        '''
        Get a data archive given an archive name

        Returns
        -------
        archive_name : str
            name of the archive to be retrieved

        '''

        return self._get_archvie(archive_name)


    def get_metadata(self, archive_name):
        '''
        Retrieve the metadata for a given archive

        Parameters
        ----------
        archive_name : str
            name of the archive to be retrieved
        
        Returns
        -------
        metadata : dict
            current archive metadata
        '''

        return self._get_archive_metadata(archive_name)


    # Private methods (to be implemented by subclasses of DataManager)
    
    def _update(self, archive_name, version_id, version_data):
        raise NotImplementedError('BaseDataManager cannot be used directly. Use a subclass, such as MongoDBManager')

    def _update_metadata(self, archive_name, **kwargs):
        raise NotImplementedError('BaseDataManager cannot be used directly. Use a subclass, such as MongoDBManager')

    def _get_services_for_version(self, archive_name, version_id):
        raise NotImplementedError('BaseDataManager cannot be used directly. Use a subclass, such as MongoDBManager')

    def _get_datafile_from_service(self, archive_name, version_id, service):
        raise NotImplementedError('BaseDataManager cannot be used directly. Use a subclass, such as MongoDBManager')

    def _get_all_version_ids(self, archive_name):
        raise NotImplementedError('BaseDataManager cannot be used directly. Use a subclass, such as MongoDBManager')

    def _create_archive(self, archive_name, **metadata):
        raise NotImplementedError('BaseDataManager cannot be used directly. Use a subclass, such as MongoDBManager')

    def _create_if_not_exists(self, archive_name, **metadata):
        raise NotImplementedError('BaseDataManager cannot be used directly. Use a subclass, such as MongoDBManager')

    def _get_archvie(self, archive_name):
        raise NotImplementedError('BaseDataManager cannot be used directly. Use a subclass, such as MongoDBManager')

    def _get_archive_metadata(self, archive_name):
        raise NotImplementedError('BaseDataManager cannot be used directly. Use a subclass, such as MongoDBManager')

    def _get_service_path(self, archive_name, version_id):
        raise NotImplementedError('BaseDataManager cannot be used directly. Use a subclass, such as MongoDBManager')
