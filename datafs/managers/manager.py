
from __future__ import absolute_import


class BaseDataManager(object):
    '''
    Base class for DataManager metadata store objects

    Should be subclassed. Not intended to be used directly.
    '''

    def __init__(self, api=None):
        self.api = api

    def update(self, archive_name, checksum, metadata):
        '''
        Register a new version for archive ``archive_name``

        .. note ::

            need to implement hash checking to prevent duplicate writes

        '''
        version_metadata = {
            "author": self.api.username,
            "contact": self.api.contact,
            "updated": self.api.create_timestamp(),
            "checksum": checksum}

        archive_data = metadata

        self.update_metadata(archive_name, archive_data)
        self._update(archive_name, version_metadata)

    def update_metadata(self, archive_name, metadata):
        '''
        Update metadata for archive ``archive_name``
        '''

        self._update_metadata(archive_name, metadata)

    def create_archive(
            self,
            archive_name,
            authority_name,
            service_path,
            raise_if_exists=True,
            metadata={}):
        '''
        Create a new data archive

        Returns
        -------
        archive : object
            new :py:class:`~datafs.core.data_archive.DataArchive` object

        '''

        metadata['creator'] = metadata.get('creator', self.api.username)
        metadata['contact'] = metadata.get('contact', self.api.contact)
        metadata['creation_date'] = metadata.get(
            'creation_date', self.api.create_timestamp())

        if raise_if_exists:
            self._create_archive(
                archive_name,
                authority_name,
                service_path,
                metadata)
        else:
            self._create_if_not_exists(
                archive_name, authority_name, service_path, metadata)

    def get_archive(self, archive_name):
        '''
        Get a data archive given an archive name

        Returns
        -------
        archive_name : str
            name of the archive to be retrieved

        '''

        return self._get_archive(archive_name)

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

    def _update(self, archive_name, archive_data):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _update_metadata(self, archive_name, metadata):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _create_archive(
            self,
            archive_name,
            authority_name,
            service_path,
            metadata):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _create_if_not_exists(
            self,
            archive_name,
            authority_name,
            service_path,
            metadata):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _get_archive(self, archive_name):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _get_archive_metadata(self, archive_name):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')
