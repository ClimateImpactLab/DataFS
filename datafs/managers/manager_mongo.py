
from __future__ import absolute_import

from datafs.managers.manager import BaseDataManager
from datafs.core.data_archive import DataArchive

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, DuplicateKeyError

import logging

class ConnectionError(IOError):
    pass

def catch_timeout(func):
    '''
    Decorator for wrapping MongoDB connections
    '''

    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ServerSelectionTimeoutError as e:
            raise ConnectionError('Connection to MongoDB server could not be established. Make sure you are running a MongoDB server and that the MongoDB Manager has been configured to connect over the correct port. For more information see https://docs.mongodb.com/manual/tutorial/.')

    return inner


class MongoDBManager(BaseDataManager):
    '''
    Parameters
    ----------
    api : object
        :py:class:`~datafs.core.data_api.DataAPI` object

    *args, **kwargs passed to :py:class:`pymongo.MongoClient`
    '''

    def __init__(self, api=None, *args, **kwargs):
        super(MongoDBManager, self).__init__(api)
        
        # setup MongoClient
        # Arguments can be passed to the client
        self._client = MongoClient(*args, **kwargs)

        self._db = None
        self._coll = None

    def _connect(self):

        self._db = self._client[self.api.DatabaseName]
        self._coll = self._db[self.api.DataTableName]

    @property
    def collection(self):
        if self._coll is None:
            self._connect()

        return self._coll

    # Private methods (to be implemented!)
    
    @catch_timeout
    def _update(self, archive_name, version_id, version_data):
        self.collection.update({"_id":archive_name}, {"$push":{"versions": version_data}})

    def _update_metadata(self, archive_name, **kwargs):
        raise NotImplementedError

    def _get_services_for_version(self, archive_name, version_id):
        raise NotImplementedError

    def _get_datafile_from_service(self, archive_name, version_id, service):
        raise NotImplementedError

    @catch_timeout
    def _get_all_version_ids(self, archive_name):
        version_doc = self.collection.find_one(
            {"_id":archive_name}, 
            projection={"versions.version_id": 1})

        return [ver["version_id"] for ver in version_doc["versions"]]


    @catch_timeout
    def _create_archive(self, archive_name, **metadata):

        doc = {'_id': archive_name, 'versions': []}
        doc.update(**metadata)

        self.collection.insert_one(doc)

    def _create_if_not_exists(self, archive_name, **metadata):

        try:
            self._create_archive(archive_name, **metadata)
        except DuplicateKeyError:
            pass

    @catch_timeout
    def _get_archive_listing(self, archive_name):
        '''
        Return full document for ``{_id:'archive_name'}``

        .. note::

            MongoDB specific results - do not expose to user
        '''

        return self.collection.find_one({'_id': archive_name})


    @catch_timeout
    def _get_all_service_paths(self, archive_name):
        
        version_doc = self.collection.find_one(
            {"_id":archive_name}, 
            projection={"versions": 1})

        return {ver['version_id']: ver['service_path'] for ver in version_doc["versions"]}


    def _get_service_path(self, archive_name, version_id):

        return self._get_all_service_paths(archive_name)[version_id]


    def _get_archive_metadata(self, archive_name):

        res = self._get_archive_listing(archive_name)
        
        return {k: v for k, v in res.items() if k not in ['_id', 'versions']}
        
    @catch_timeout
    def _get_archive(self, archive_name):

        res = self.collection.find_one({'_id': archive_name})
        
        return DataArchive(api = self.api, archive_name=res['_id'])

        
