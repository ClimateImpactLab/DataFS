

from datafs.managers.manager import BaseDataManager


class DynamoDBManager(BaseDataManager):

    def __init__(self, api, *args, **kwargs):
        super(DynamoDBManager, self).__init__(api)

    # Private methods (to be implemented!)

    def _update(self, archive_name, version_id, version_data):
        raise NotImplementedError

    def _update_metadata(self, archive_name, **kwargs):
        raise NotImplementedError

    def _get_services_for_version(self, archive_name, version_id):
        raise NotImplementedError

    def _get_datafile_from_service(self, archive_name, version_id, service):
        raise NotImplementedError

    def _get_all_version_ids(self, archive_name):
        raise NotImplementedError

    def _create_archive(self, archive_name):
        raise NotImplementedError

    def _create_if_not_exists(self, archive_name, **metadata):
        raise NotImplementedError

    def _get_archive(self, archive_name):
        raise NotImplementedError
