from datafs import DataAPI
from datafs.core.data_archive import DataArchive
from datafs.managers.manager_dynamo import DynamoDBManager
from fs.s3fs import S3FS
from fs.osfs import OSFS

import tempfile
import shutil


tmpdir = tempfile.mkdtemp()


class MyArchive(DataArchive):

    def delete(self):
        raise IOError('Data archives cannot be deleted')


class MyAPI(DataAPI):

    _ArchiveConstructor = MyArchive
    '''
    ``MyArchive`` objects will be created instead of ``DataArchive`` objects
    '''

    def __init__(self, AWS_ACCESS_KEY, AWS_SECRET_KEY, *args, **kwargs):
        super(MyAPI, self).__init__(*args, **kwargs)

        # pre-configure the API with your organization's setup

        manager = DynamoDBManager(
            table_name='project_data',
            session_args={
                'aws_access_key_id': AWS_ACCESS_KEY,
                'aws_secret_access_key': AWS_SECRET_KEY},
            resource_args={
                'endpoint_url': 'http://localhost:8000/',
                'region_name': 'us-east-1'})

        if 'project_data' in manager.table_names:
            manager.delete_table('project_data')

        manager.create_archive_table('project_data', raise_on_err=False)

        self.attach_manager(manager)

        # Prevent changes to the manager configuration
        self.lock_manager()

        s3_bucket1 = S3FS(
            'org-bucket-1',
            aws_access_key=AWS_ACCESS_KEY,
            aws_secret_key=AWS_SECRET_KEY)

        s3_bucket2 = S3FS(
            'org-bucket-2',
            aws_access_key=AWS_ACCESS_KEY,
            aws_secret_key=AWS_SECRET_KEY)

        network_storage = OSFS(tmpdir)

        self.attach_authority('s3-1', s3_bucket1)
        self.attach_authority('s3-2', s3_bucket2)
        self.attach_authority('NAT-1', network_storage)

        # Prevent changes to the set of authorities
        self.lock_authorities()


def teardown():
    shutil.rmtree(tmpdir)
