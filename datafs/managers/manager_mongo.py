
from __future__ import absolute_import

from datafs.managers.manager import BaseDataManager

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


class MongoDBManager(BaseDataManager):
    '''
    Parameters
    ----------

    database_name : str
        Name of the database containing the DataFS tables

    table_name: str
        Name of the data archive table

    client_kwargs : dict
        Keyword arguments used in initializing a
        :py:class:`pymongo.MongoClient` object
    '''

    def __init__(self, database_name, table_name, client_kwargs=None):
        super(MongoDBManager, self).__init__(table_name)

        if client_kwargs is None:
            client_kwargs = {}

        # setup MongoClient
        # Arguments can be passed to the client
        self._client_kwargs = client_kwargs
        self._client = MongoClient(**client_kwargs)

        self._database_name = database_name

        self._db = None
        self._coll = None
        self._spec_coll = None

    @property
    def config(self):
        config = {
            'database_name': self._database_name,
            'table_name': self._table_name,
            'client_kwargs': self._client_kwargs
        }

        return config

    @property
    def database_name(self):
        return self._database_name

    @property
    def table_name(self):
        return self._table_name

    def _get_table_names(self):
        return self.db.collection_names(include_system_collections=False)

    def _create_archive_table(self, table_name):
        if table_name in self._get_table_names():
            raise KeyError('Table "{}" already exists'.format(table_name))

        self.db.create_collection(table_name)

    def _delete_table(self, table_name):
        if table_name not in self._get_table_names():
            raise KeyError('Table "{}" not found'.format(table_name))

        self.db.drop_collection(table_name)

    @property
    def collection(self):
        table_name = self.table_name

        if table_name not in self._get_table_names():
            raise KeyError('Table "{}" not found'.format(table_name))

        return self.db[table_name]

    @property
    def spec_collection(self):

        spec_table_name = self._spec_table_name

        if spec_table_name not in self._get_table_names():
            raise KeyError('Table "{}" not found'.format(spec_table_name))

        return self.db[spec_table_name]

    @property
    def db(self):
        if self._db is None:
            self._db = self._client[self.database_name]

        return self._db

    # Private methods (to be implemented!)

    def _update(self, archive_name, version_metadata):
        self.collection.update(
            {"_id": archive_name},
            {"$push": {"version_history": version_metadata}})

    def _update_metadata(self, archive_name, archive_metadata):

        for key, val in archive_metadata.items():

            if val is None:
                self.collection.update(
                    {"_id": archive_name},
                    {"$unset": {"archive_metadata.{}".format(key): ""}})

            else:
                self.collection.update(
                    {"_id": archive_name},
                    {"$set": {"archive_metadata.{}".format(key): val}})

    def _update_spec_config(self, document_name, spec):

        self.spec_collection.update_many(
            {"_id": document_name},
            {"$set": {'config': spec}}, upsert=True)

    def _create_archive(
            self,
            archive_name,
            metadata):

        try:
            self.collection.insert_one(metadata)
        except DuplicateKeyError:
            raise KeyError('Archive "{}" already exists'.format(archive_name))

    def _create_spec_config(self, table_name, spec_documents):

        if self._spec_coll is None:
            self._spec_coll = self.db[table_name + '.spec']

        self.spec_collection.insert_many(spec_documents)

    def _get_archive_listing(self, archive_name):
        '''
        Return full document for ``{_id:'archive_name'}``

        .. note::

            MongoDB specific results - do not expose to user
        '''

        res = self.collection.find_one({'_id': archive_name})

        if res is None:
            raise KeyError

        return res

    def _batch_get_archive_listing(self, archive_names):
        '''
        Batched version of :py:meth:`~MongoDBManager._get_archive_listing`

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

        res = self.collection.find({'_id': {'$in': list(archive_names)}})

        if res is None:
            res = []

        return res

    def _delete_archive_record(self, archive_name):

        return self.collection.remove({'_id': archive_name})

    def _search(self, search_terms, begins_with=None):

        if len(search_terms) == 0:
            query = {}
        elif len(search_terms) == 1:
            query = {'tags': {'$in': [search_terms[0]]}}
        else:
            query = {
                '$and': [{'tags': {'$in': [tag]}} for tag in search_terms]}

        res = self.collection.find(query, {"_id": 1})

        for r in res:
            if (not begins_with) or r['_id'].startswith(begins_with):
                yield r['_id']

    def _set_tags(self, archive_name, updated_tag_list):

        self.collection.update(
            {"_id": archive_name},
            {"$set": {"tags": updated_tag_list}})

    def _get_spec_documents(self, table_name):
        return [item for item in self.spec_collection.find({})]
