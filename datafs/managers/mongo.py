
from __future__ import absolute_import

from datafs.managers.manager import BaseDataManager
from datafs.core.data_archive import DataArchive

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

import logging

class MongoDBConnectionError(IOError):
    message = 'Connection to MongoDB server could not be established. Make sure you are running a MongoDB and that the MongoDB Manager has been configured to connect over the correct port. For more information see https://docs.mongodb.com/manual/tutorial/.'

class MongoDBManager(BaseDataManager):
    def __init__(self, api, *args, **kwargs):
        super(MongoDBManager, self).__init__(api)
        
        # setup MongoClient
        # Arguments can be passed to the client
        self._client = MongoClient(*args, **kwargs)

        self.db = self._client[self.api.DatabaseName]
        self.coll = self.db[self.api.DataTableName]


    # Private methods (to be implemented!)
    
    def _update(self, archive_name, file, **kwargs):
        raise NotImplementedError

    def _update_metadata(self, archive_name, **kwargs):
        raise NotImplementedError

    def _get_services_for_version(self, archive_name, version_id):
        raise NotImplementedError

    def _get_datafile_from_service(self, archive_name, version_id, service):
        raise NotImplementedError

    def _get_all_version_ids(self, archive_name):
        raise NotImplementedError

    def _create_archvie(self, archive_name, **metadata):
        '''
        .. todo ::
            This should raise an error if exists!!
        '''

        doc = {'_id': archive_name, 'versions': []}
        doc.update(**metadata)

        try:
            self.coll.find_one_and_replace({'_id': archive_name}, doc, upsert=True)
        except ServerSelectionTimeoutError as e:
            raise MongoDBConnectionError(MongoDBConnectionError.message)

    def _get_archive_metadata(self, archive_name):
        try:
            res = self.coll.find_one({'_id': archive_name})
        except ServerSelectionTimeoutError as e:
            raise MongoDBConnectionError(MongoDBConnectionError.message)
        
        return {k: v for k, v in res.items() if k not in ['_id', 'versions']}
        
    def _get_archvie(self, archive_name):

        try:
            res = self.coll.find_one({'_id': archive_name})
        except ServerSelectionTimeoutError as e:
            raise MongoDBConnectionError(MongoDBConnectionError.message)
        
        return DataArchive(api = self.api, archive_name=res['_id'])

        
