
from __future__ import absolute_import

import time, threading



class BaseDataManager(object):
    '''
    Base class for DataManager metadata store objects

    Should be subclassed. Not intended to be used directly.
    '''

    REQUIRED_USER_CONFIG = {}

    REQUIRED_ARCHIVE_METADATA = {}

    TimestampFormat = '%Y%m%d-%H%M%S'

    def __init__(self, table_name):
        
        self._table_name = table_name
        self._spec_table_name = table_name + '.spec'

        self._required_user_config = None
        self._required_archive_metadata = None

    @property
    def table_names(self):
        return self._get_table_names()

    @property
    def required_user_config(self):
        if self._required_user_config is None:
            user_config = self._get_required_user_config()
            assert isinstance(user_config, dict), 'sorry, user_config "{}" is a {}'.format(user_config, type(user_config))

            self._required_user_config = user_config

        return self._required_user_config


    @property
    def required_archive_metadata(self):
        if self._required_archive_metadata is None:
            archive_metadata = self._get_required_archive_metadata()
            assert isinstance(archive_metadata, dict)

            self._required_archive_metadata = archive_metadata

        return self._required_archive_metadata


    def create_archive_table(self, table_name, raise_on_err=True):
        '''

        Parameters
        -----------
        table_name: str

        Creates a table to store archives for your project
        Also creates and populates a table with basic spec for user and metadata config

        Returns
        -------
        None


        '''
        

        
        if raise_on_err:
            self._create_archive_table(table_name)
            self._create_spec_table(table_name)
            self._create_spec_config(table_name)
            

        else:
            try:
                self._create_archive_table(table_name)
                self._create_spec_table(table_name)
                self._create_spec_config(table_name)
            except KeyError:
                pass

    def update_spec_config(self, document_name,spec):
        '''
        Allows update to default setting of either user config or metadata config
        One or the other must be selected as True.

        Parameters:
        table_name: str
        user_config: bool
        metadata_config: bool
        **spec: kwargs

        '''


        self._update_spec_config(document_name, spec)


    def delete_table(self, table_name, raise_on_err=True):
        if raise_on_err:
            self._delete_table(table_name)
        else:
            try:
                self._delete_table(table_name)
            except KeyError:
                pass

    def update(self, archive_name, checksum, metadata, user_config={}, **kwargs):
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
        version_metadata.update(kwargs)

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

        required = set(self.required_user_config.keys())
        required |= set(self.required_archive_metadata.keys())

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
    def _create_spec_table(self, table_name):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _create_spec_config(self, table_name):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _update_spec_config(self, document_name, spec):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')        

    def _delete_table(self, table_name):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _get_required_user_config(self):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _get_required_archive_metadata(self):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _get_versions(self, archive_name):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')
    def _get_document_count(self, table_name):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')


