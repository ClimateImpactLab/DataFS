.. _tutorial-sublcassing

Subclassing DataFS
==================


.. code-block:: python

    from datafs import DataAPI
    from datafs.core.data_archive import DataArchive
    from datafs.managers.manager_dynamo import DynamoDBManager
    from fs.s3fs import S3FS

    from datavar import DataVariable

    class CILArchive(DataArchive):

        def delete(self):
            raise IOError('Data archives cannot be deleted')


    class CILApi(DataAPI):

        _ArchiveConstructor = CILArchive

        def __init__(self):
            super(CILApi, self).__init__()

            # pre-configure the API with your organization's setup

            manager = DynamoDBManager(
                table_name = 'project_data', 
                profile_name = 'my_organization_profile')

            self.attach_manager(manager)
            self.lock_manager()

            s3 = S3FS(
                'MyBucket', 
                profile_name='my_organization_profile')

            self.attach_authority('s3', s3)
            self.lock_authorities()


.. code-block:: python

    cil_api = CILApi('my name')
    archive = cil_api.get_archive('arch_name')
    archive.delete()



