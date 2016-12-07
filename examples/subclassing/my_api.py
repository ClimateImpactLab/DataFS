from datafs import DataAPI
from datafs.core.data_archive import DataArchive
from datafs.managers.manager_dynamo import DynamoDBManager
from fs.s3fs import S3FS


class MyArchive(DataArchive):

    def delete(self):
        raise IOError('Data archives cannot be deleted')


class MyAPI(DataAPI):

    _ArchiveConstructor = MyArchive
    '''
    ``MyArchive`` objects will be created instead of ``DataArchive`` objects
    '''

    def __init__(self):
        super(MyAPI, self).__init__()

        # pre-configure the API with your organization's setup

        manager = DynamoDBManager(
            table_name = 'project_data', 
            profile_name = 'my_organization_profile')

        self.attach_manager(manager)

        # Prevent changes to the manager configuration
        self.lock_manager()


        s3_bucket1 = S3FS(
            'my-bucket-1', 
            profile_name='my_organization_profile')

        s3_bucket2 = S3FS(
            'my-bucket-2', 
            profile_name='my_organization_profile')

        self.attach_authority('s3-1', s3_bucket1)
        self.attach_authority('s3-2', s3_bucket2)

        # Prevent changes to the set of authorities
        self.lock_authorities()