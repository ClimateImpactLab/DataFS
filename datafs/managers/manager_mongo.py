
from __future__ import absolute_import

from datafs.managers.manager import BaseDataManager
from datafs.core.data_archive import DataArchive

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, DuplicateKeyError


class ConnectionError(IOError):
    pass


def catch_timeout(func):
    '''
    Decorator for wrapping MongoDB connections
    '''

    def inner(*args, **kwargs):
        msg = 'Connection to MongoDB server could not be established. '\
            'Make sure you are running a MongoDB server and that the MongoDB '\
            'Manager has been configured to connect over the correct port. '\
            'For more information see '\
            'https://docs.mongodb.com/manual/tutorial/.'
        try:
            return func(*args, **kwargs)
        except ServerSelectionTimeoutError:
            raise ConnectionError(msg)

    return inner


class MongoDBManager(BaseDataManager):
    '''
    Parameters
    ----------
    api : object
        :py:class:`~datafs.core.data_api.DataAPI` object

    *args, **kwargs passed to :py:class:`pymongo.MongoClient`
    '''

    def __init__(self, database_name, table_name, api=None, *args, **kwargs):
        super(MongoDBManager, self).__init__(api)

        # setup MongoClient
        # Arguments can be passed to the client
        self._client = MongoClient(*args, **kwargs)

        self._database_name = database_name
        self._table_name = table_name

        self._db = None
        self._coll = None

    @property
    def database_name(self):
        return self._database_name

    @property
    def table_name(self):
        return self._table_name

    @property
    def collection(self):
        if self._coll is None:
            self._connect()

        return self._coll

    def _connect(self):

        self._db = self._client[self.database_name]
        self._coll = self._db[self.table_name]

    # Private methods (to be implemented!)

    @catch_timeout
    def _update(self, archive_name, archive_data):
        self.collection.update({"_id": archive_name},
                               {"$push": {"versions": archive_data}})

    def _update_metadata(self, archive_name, metadata):
        for key, val in metadata.items():
            self.collection.update({"_id": archive_name},
                                   {"$set": {"metadata.{}".format(key): val}})

    @catch_timeout
    def _create_archive(
            self,
            archive_name,
            authority_name,
            service_path,
            metadata):

        doc = {
            '_id': archive_name,
            'authority_name': authority_name,
            'service_path': service_path,
            'versions': []}
        doc['metadata'] = metadata

        try:
            self.collection.insert_one(doc)
        except DuplicateKeyError:
            raise KeyError('Archive "{}" already exists'.format(archive_name))

    def _create_if_not_exists(
            self,
            archive_name,
            authority_name,
            service_path,
            metadata):

        try:
            self._create_archive(
                archive_name,
                authority_name,
                service_path,
                metadata)
        except KeyError:
            pass

    @catch_timeout
    def _get_archive_listing(self, archive_name):
        '''
        Return full document for ``{_id:'archive_name'}``

        .. note::

            MongoDB specific results - do not expose to user
        '''

        return self.collection.find_one({'_id': archive_name})

    def _get_authority_name(self, archive_name):

        res = self._get_archive_listing(archive_name)

        return res['authority_name']

    def _get_service_path(self, archive_name):

        res = self._get_archive_listing(archive_name)

        return res['service_path']


    def _get_archive_metadata(self, archive_name):

        res = self._get_archive_listing(archive_name)

        return res['metadata']

    def _get_versions(self, archive_name):

        res = self.collection.find_one({'_id': archive_name})

        return res['versions']

    def _get_latest_hash(self, archive_name):

        versions = self._get_versions(archive_name)

        if len(versions) == 0:
            return None

        else:
            return versions[-1]['checksum']
