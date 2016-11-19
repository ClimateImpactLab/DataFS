

from .datafs.managers.manager import BaseDataManager
from pymongo import MongoClient

class MongoDBManager(BaseDataManager):
    def __init__(self, api, *args, **kwargs):
        super(MongoDBManager, self).__init__(api)
        self._client = MongoClient()

        self.db = api[self.api.DatabaseName]
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
        doc = {'archive_name': archive_name, 'versions': []}
        doc.update(**metadata)

        self.coll.insert(doc)

    def _get_archvie(self, archive_name):
        
        self.coll.find_one({'archive_name': archive_name})