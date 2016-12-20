
from __future__ import absolute_import


class BaseDataManager(object):
    '''
    Base class for DataManager metadata store objects

    Should be subclassed. Not intended to be used directly.
    '''

    def __init__(self, api=None):
        self.api = api

    @property
    def table_names(self):
        return self._get_table_names()

    def create_archive_table(self, table_name, raise_on_err=True):
        if raise_on_err:
            self._create_archive_table(table_name)

        else:
            try:
                self._create_archive_table(table_name)
            except KeyError:
                pass

    def delete_table(self, table_name, raise_on_err=True):
        if raise_on_err:
            self._delete_table(table_name)
        else:
            try:
                self._delete_table(table_name)
            except KeyError:
                pass

    def update(self, archive_name, checksum, metadata):
        '''
        Register a new version for archive ``archive_name``

        .. note ::

            need to implement hash checking to prevent duplicate writes

        '''
        version_metadata = {
            'updated': self.api.create_timestamp(),
            'algorithm': checksum['algorithm'],
            'checksum': checksum['checksum']}

        version_metadata.update(self.api.user_config)

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
            raise_on_err=True,
            metadata={}):
        '''
        Create a new data archive

        Returns
        -------
        archive : object
            new :py:class:`~datafs.core.data_archive.DataArchive` object

        '''

        archive_metadata = {}
        archive_metadata.update(self.api.user_config)
        archive_metadata.update(metadata)

        archive_metadata['creation_date'] = archive_metadata.get(
            'creation_date', self.api.create_timestamp())

        required = set(self.api.REQUIRED_USER_CONFIG.keys())
        required |= set(self.api.REQUIRED_ARCHIVE_METADATA.keys())

        for attr in required:
            assert attr in archive_metadata, 'Required attribute "{}" missing from metadata'.format(
                attr)

        if raise_on_err:
            self._create_archive(
                archive_name,
                authority_name,
                service_path,
                archive_metadata)
        else:
            self._create_if_not_exists(
                archive_name, authority_name, service_path, archive_metadata)

        return self.get_archive(archive_name)

    def get_archive(self, archive_name):
        '''
        Get a data archive given an archive name

        Returns
        -------
        archive_name : str
            name of the archive to be retrieved

        '''

        try:
            authority_name = self._get_authority_name(archive_name)
            service_path = self._get_service_path(archive_name)

        except KeyError:
            raise KeyError('Archive "{}" not found'.format(archive_name))

        return self.api._ArchiveConstructor(
            api=self.api,
            archive_name=archive_name,
            authority=authority_name,
            service_path=service_path)

    def get_archives(self):
        '''
        Returns a list of DataArchive objects

        '''
        return [self.get_archive(arch) for arch in self.get_archive_names()]

    def get_archive_names(self):
        '''
        Returns a list of DataArchive names

        '''
        return self._get_archive_names()

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

    def get_latest_hash(self, archive_name):
        '''
        Retrieve the file hash for a given archive

        Parameters
        ----------
        archive_name : str
            name of the archive for which to retrieve the hash

        Returns
        -------
        hashval : str
            hash value for the latest version of archive_name

        '''

        return self._get_latest_hash(archive_name)

    def delete_archive_record(self, archive_name):
        '''
        Deletes an archive from the database

        Parameters
        ----------

        archive_name : str
            name of the archive to delete

        '''

        self._delete_archive_record(archive_name)

    def get_versions(self, archive_name):
        return self._get_versions(archive_name)

    # Private methods (to be implemented by subclasses of DataManager)

    def _update(self, archive_name, archive_data):
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

    def _get_archives(self):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _get_archive_metadata(self, archive_name):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _get_latest_hash(self, archive_name):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _get_authority_name(self, archive_name):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _get_service_path(self, archive_name):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _delete_archive_record(self, archive_name):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _get_table_names(self):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _create_archive_table(self, table_name):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _delete_table(self, table_name):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _get_versions(self, archive_name):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')
