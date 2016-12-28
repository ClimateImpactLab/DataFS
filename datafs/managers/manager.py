
from __future__ import absolute_import

import time



class BaseDataManager(object):
    '''
    Base class for DataManager metadata store objects

    Should be subclassed. Not intended to be used directly.
    '''

    REQUIRED_USER_CONFIG = {
    }

    REQUIRED_ARCHIVE_METADATA = {
    }

    TimestampFormat = '%Y%m%d-%H%M%S'

    def __init__(self):
        pass

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

    def update(self, archive_name, checksum, metadata, user_config={}):
        '''
        Register a new version for archive ``archive_name``

        .. note ::

            need to implement hash checking to prevent duplicate writes

        '''
        version_metadata = {
            'updated': self.create_timestamp(),
            'algorithm': checksum['algorithm'],
            'checksum': checksum['checksum']}

        version_metadata.update(user_config)

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
            archive_path,
            versioned,
            raise_on_err=True,
            metadata={},
            user_config={}):
        '''
        Create a new data archive

        Returns
        -------
        archive : object
            new :py:class:`~datafs.core.data_archive.DataArchive` object

        '''

        archive_metadata = {}
        archive_metadata.update(user_config)
        archive_metadata.update(metadata)

        archive_metadata['creation_date'] = archive_metadata.get(
            'creation_date', self.create_timestamp())

        required = set(self.REQUIRED_USER_CONFIG.keys())
        required |= set(self.REQUIRED_ARCHIVE_METADATA.keys())

        for attr in required:
            assert attr in archive_metadata, 'Required attribute "{}" missing from metadata'.format(
                attr)

        if raise_on_err:
            self._create_archive(
                archive_name,
                authority_name,
                archive_path,
                versioned,
                archive_metadata)
        else:
            self._create_if_not_exists(
                archive_name, 
                authority_name, 
                archive_path, 
                versioned, 
                archive_metadata)

        return self.get_archive(archive_name)

    def get_archive(self, archive_name):
        '''
        Get a data archive given an archive name

        Returns
        -------
        archive_specification : dict
            archive_name: name of the archive to be retrieved
            authority: name of the archive's authority
            archive_path: service path of archive 
        '''

        try:
            spec = self._get_archive_spec(archive_name)
            spec['archive_name'] = archive_name
            return spec

        except KeyError:
            raise KeyError('Archive "{}" not found'.format(archive_name))


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


    @classmethod
    def create_timestamp(cls):
        '''
        Utility function for formatting timestamps

        Overload this function to change timestamp formats
        '''

        return time.strftime(cls.TimestampFormat, time.gmtime())


    # Private methods (to be implemented by subclasses of DataManager)

    def _update(self, archive_name, archive_data):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _create_archive(
            self,
            archive_name,
            authority_name,
            archive_path,
            versioned,
            metadata):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _create_if_not_exists(
            self,
            archive_name,
            authority_name,
            archive_path,
            versioned,
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

    def _get_archive_path(self, archive_name):
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
