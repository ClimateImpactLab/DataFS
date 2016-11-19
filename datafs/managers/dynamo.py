

from datafs.managers.manager import BaseDataManager


class DynamoDBManager(BaseDataManager):
    def __init__(self, *args, **kwargs):
        super(DynamoDBManager, self).__init__(*args, **kwargs)


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

    def _create_archvie(self, archive_name):
        raise NotImplementedError

    def _get_archvie(self, archive_name):
        raise NotImplementedError
