

from manager import BaseDataManager


class MongoDB(BaseDataManager):
    def __init__(self, *args, **kwargs):
        super(MongoDB, self).__init__(*args, **kwargs)

    @property
    def latest(self):
        raise NotImplementedError

    @property
    def version_ids(self):
        raise NotImplementedError

    def _get_version_from_service(self, version_id, service):
        raise NotImplementedError

    def update(self, service, service_object):
        raise NotImplementedError

    def _get_all_version_ids(self):
        raise NotImplementedError