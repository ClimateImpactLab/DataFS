

from .datafs.services.service import DataService
from .datafs.core.data_file import DataFile
from fs.s3fs import S3FS


class S3Service(DataService):
    '''
    Access files & directories stored on Amazon S3 storage
    '''
    
    FileConstructor = S3DataFile

    def __init__(self, api, archive, *args, **kwargs):
        DataService.__init__(self, api, archive, *args, **kwargs)

    def self._get_datafile(self, archive_name, version_id):
        raise NotImplementedError


class S3DataFile(DataFile, S3FS):
    '''
    S3FS access files & directories stored on Amazon S3 storage
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        S3FS.__init__(self, *args, **kwargs)

