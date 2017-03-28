
from __future__ import absolute_import

import time
from datafs.config.helpers import check_requirements


class BaseDataManager(object):
    '''
    Base class for DataManager metadata store objects

    Should be subclassed. Not intended to be used directly.
    '''

    TimestampFormat = '%Y%m%d-%H%M%S'

    def __init__(self, table_name):

        self._table_name = table_name
        self._spec_table_name = table_name + '.spec'

        self._required_user_config = None
        self._required_archive_metadata = None
        self._valid_top_level_domains = None
        self._required_archive_patterns = None

    @property
    def table_names(self):
        return self._get_table_names()

    @property
    def required_user_config(self):
        if self._required_user_config is None:
            self._refresh_spec()

        return self._required_user_config

    @property
    def required_archive_metadata(self):
        if self._required_archive_metadata is None:
            self._refresh_spec()

        return self._required_archive_metadata

    @property
    def required_archive_patterns(self):
        if self._required_archive_patterns is None:
            self._refresh_spec()

        return self._required_archive_patterns

    def _refresh_spec(self):
        spec_documents = self._get_spec_documents(self._table_name)

        spec = {d['_id']: d['config'] for d in spec_documents}

        self._required_user_config = spec['required_user_config']
        self._required_archive_metadata = spec['required_archive_metadata']
        self._required_archive_patterns = spec['required_archive_patterns']

    def create_archive_table(self, table_name, raise_on_err=True):
        '''

        Parameters
        -----------
        table_name: str

        Creates a table to store archives for your project
        Also creates and populates a table with basic spec for user and
        metadata config

        Returns
        -------
        None


        '''

        spec_documents = [
            {'_id': 'required_user_config', 'config': {}},
            {'_id': 'required_archive_metadata', 'config': {}},
            {'_id': 'required_archive_patterns', 'config': []}]

        if raise_on_err:
            self._create_archive_table(table_name)
            self._create_archive_table(table_name+'.spec')
            self._create_spec_config(table_name, spec_documents)

        else:
            try:
                self._create_archive_table(table_name)
                self._create_archive_table(table_name+'.spec')
                self._create_spec_config(table_name, spec_documents)
            except KeyError:
                pass

    def update_spec_config(self, document_name, spec):
        '''
        Set the contents of a specification document by name

        This method should not be used directly. Instead, use
        :py:meth:`set_required_user_config` or
        :py:meth:`set_required_archive_metadata`.

        Parameters:
        document_name : str

            Name of a specification document's key

        spec : dict

            Dictionary metadata specification

        '''

        self._update_spec_config(document_name, spec)

    def set_required_user_config(self, user_config):
        '''
        Sets required user metadata for all users

        Parameters
        ----------
        user_config : dict

            Dictionary of required user metadata and metadata field
            descriptions. All archive creation and update actions will be
            required to have these keys in the user_config metadata.

            If the archive or version metadata does not contain these keys, an
            error will be raised with the descrtiption in the value associated
            with the key.

        '''

        self.update_spec_config('required_user_config', user_config)
        self._required_user_config = None

    def set_required_archive_metadata(self, metadata_config):
        '''
        Sets required archive metatdata for all users

        Parameters
        ----------
        metadata_config : dict

            Dictionary of required archive metada and metadata field
            descriptions. All archives created on this manager table will
            be required to have these keys in their archive's metadata.

            If the archive metadata does not contain these keys, an error
            will be raised with the description in the value associated with
            the key.

        '''

        self.update_spec_config('required_archive_metadata', metadata_config)
        self._required_archive_metadata = None

    def set_required_archive_patterns(self, required_archive_patterns):
        '''
        Sets archive_name regex patterns for the enforcement of naming
        conventions on archive creation

        Parameters
        ----------
        required_archive_patterns: strings  of args
        '''
        self.update_spec_config('required_archive_patterns',
                                required_archive_patterns)
        self._required_archive_patterns = None

    def delete_table(self, table_name=None, raise_on_err=True):
        if table_name is None:
            table_name = self._table_name

        if table_name not in self._get_table_names():
            if raise_on_err:
                raise KeyError('Table "{}" not found'.format(table_name))

        else:
            self._delete_table(table_name)

        if table_name + '.spec' not in self._get_table_names():
            if raise_on_err:
                raise KeyError(
                    'Table "{}.spec" not found'.format(table_name + '.spec'))

        else:
            self._delete_table(table_name + '.spec')

    def update(self, archive_name, version_metadata):
        '''
        Register a new version for archive ``archive_name``

        .. note ::

            need to implement hash checking to prevent duplicate writes
        '''
        version_metadata['updated'] = self.create_timestamp()
        version_metadata['version'] = str(
            version_metadata.get('version', None))

        self._update(archive_name, version_metadata)

    def update_metadata(self, archive_name, archive_metadata):
        '''
        Update metadata for archive ``archive_name``
        '''

        required_metadata_keys = self.required_archive_metadata.keys()
        for key, val in archive_metadata.items():
            if key in required_metadata_keys and val is None:
                raise ValueError(
                    'Cannot remove required metadata attribute "{}"'.format(
                        key))

        self._update_metadata(archive_name, archive_metadata)

    def create_archive(
            self,
            archive_name,
            authority_name,
            archive_path,
            versioned,
            raise_on_err=True,
            metadata=None,
            user_config=None,
            tags=None,
            helper=False):
        '''
        Create a new data archive

        Returns
        -------
        archive : object
            new :py:class:`~datafs.core.data_archive.DataArchive` object

        '''

        archive_metadata = self._create_archive_metadata(
            archive_name=archive_name,
            authority_name=authority_name,
            archive_path=archive_path,
            versioned=versioned,
            raise_on_err=raise_on_err,
            metadata=metadata,
            user_config=user_config,
            tags=tags,
            helper=helper)

        if raise_on_err:
            self._create_archive(
                archive_name,
                archive_metadata)
        else:
            self._create_if_not_exists(
                archive_name,
                archive_metadata)

        return self.get_archive(archive_name)

    def _create_archive_metadata(
            self,
            archive_name,
            authority_name,
            archive_path,
            versioned,
            raise_on_err=True,
            metadata=None,
            user_config=None,
            tags=None,
            helper=False):

        if metadata is None:
            metadata = {}

        if user_config is None:
            user_config = {}

        if tags is None:
            tags = []

        check_requirements(
            to_populate=user_config,
            prompts=self.required_user_config,
            helper=helper)

        check_requirements(
            to_populate=metadata,
            prompts=self.required_archive_metadata,
            helper=helper)

        archive_metadata = {
            '_id': archive_name,
            'authority_name': authority_name,
            'archive_path': archive_path,
            'versioned': versioned,
            'version_history': [],
            'archive_metadata': metadata,
            'tags': tags
        }
        archive_metadata.update(user_config)

        archive_metadata['creation_date'] = archive_metadata.get(
            'creation_date', self.create_timestamp())

        return archive_metadata

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
            return spec

        except KeyError:
            raise KeyError('Archive "{}" not found'.format(archive_name))

    def batch_get_archive(self, archive_names):
        '''
        Batched version of :py:meth:`~DynamoDBManager._get_archive_listing`

        Returns a list of full archive listings from an iterable of archive
        names

        .. note ::

            Invalid archive names will simply not be returned, so the response
            may not be the same length as the supplied `archive_names`.

        Parameters
        ----------

        archive_names : list

            List of archive names

        Returns
        -------

        archive_listings : list

            List of archive listings

        '''

        return map(
            self._format_archive_listing_as_constructor_spec,
            self._batch_get_archive_listing(archive_names))

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

    def get_version_history(self, archive_name):
        return self._get_version_history(archive_name)

    @classmethod
    def create_timestamp(cls):
        '''
        Utility function for formatting timestamps

        Overload this function to change timestamp formats
        '''

        return time.strftime(cls.TimestampFormat, time.gmtime())

    def search(self, search_terms, begins_with=None):
        '''

        Parameters
        ----------
        search_terms: str
            strings of terms to search for

            If called as `api.manager.search()`, `search_terms` should be a
            list or a tuple of strings

        '''

        return self._search(search_terms, begins_with=begins_with)

    def get_tags(self, archive_name):
        '''
        Returns the list of tags associated with an archive
        '''

        return self._get_tags(archive_name)

    def add_tags(self, archive_name, tags):
        '''
        Add tags to an archive

        Parameters
        ----------
        archive_name:s tr
            Name of archive

        tags: list or tuple of strings
            tags to add to the archive

        '''
        updated_tag_list = list(self._get_tags(archive_name))
        for tag in tags:
            if tag not in updated_tag_list:
                updated_tag_list.append(tag)

        self._set_tags(archive_name, updated_tag_list)

    def delete_tags(self, archive_name, tags):
        '''
        Delete tags from an archive

        Parameters
        ----------
        archive_name:s tr
            Name of archive

        tags: list or tuple of strings
            tags to delete from the archive

        '''
        updated_tag_list = list(self._get_tags(archive_name))
        for tag in tags:
            if tag in updated_tag_list:
                updated_tag_list.remove(tag)

        self._set_tags(archive_name, updated_tag_list)

    def _get_archive_spec(self, archive_name):
        res = self._get_archive_listing(archive_name)

        if res is None:
            raise KeyError

        return self._format_archive_listing_as_constructor_spec(res)

    @staticmethod
    def _format_archive_listing_as_constructor_spec(res):

        res['archive_name'] = res.pop('_id')

        spec = ['archive_name', 'authority_name', 'archive_path', 'versioned']

        return {k: v for k, v in res.items() if k in spec}

    def _get_archive_metadata(self, archive_name):

        return self._get_archive_listing(archive_name)['archive_metadata']

    def _get_authority_name(self, archive_name):

        return self._get_archive_listing(archive_name)['authority_name']

    def _get_archive_path(self, archive_name):

        return self._get_archive_listing(archive_name)['archive_path']

    def _get_version_history(self, archive_name):

        return self._get_archive_listing(archive_name)['version_history']

    def _get_tags(self, archive_name):

        return self._get_archive_listing(archive_name)['tags']

    def _get_latest_hash(self, archive_name):

        version_history = self._get_version_history(archive_name)

        if len(version_history) == 0:
            return None

        else:
            return version_history[-1]['checksum']

    def _create_if_not_exists(
            self,
            archive_name,
            metadata):

        try:
            self._create_archive(
                archive_name,
                metadata)

        except KeyError:
            pass

    # Private methods (to be implemented by subclasses of DataManager)

    def _get_archive_listing(self, archive_name):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _update(self, archive_name, version_metadata):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _create_archive(
            self,
            archive_name,
            archive_metadata):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _get_archives(self):
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

    def _create_spec_config(self, table_name, spec_documents):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _update_spec_config(self, document_name, spec):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _delete_table(self, table_name):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _search(self, search_terms, begins_with=None):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')

    def _set_tags(self, archive_name, updated_tag_list):
        raise NotImplementedError(
            'BaseDataManager cannot be used directly. Use a subclass.')
