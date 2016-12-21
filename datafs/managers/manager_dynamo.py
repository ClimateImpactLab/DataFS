import boto3
#import botocore.exceptions.ClientError

from datafs.managers.manager import BaseDataManager


class DynamoDBManager(BaseDataManager):

    """
    Parameters
    ----------
    api : object
        :py:class:`~datafs.core.data_api.DataAPI` object
    table_name: str
        For Climate Impact Lab table_name = "cil-data"

    """

    def __init__(
            self,
            table_name,
            api=None,
            session_args={},
            resource_args={}):
        super(DynamoDBManager, self).__init__(api)

        self._table_name = table_name
        self._session_args = session_args
        self._resource_args = resource_args

        self._session = boto3.Session(**session_args)
        self._resource = self._session.resource('dynamodb', **resource_args)
        self._table = self._resource.Table(table_name)

    @property
    def config(self):
        config = {
            'table_name': self._table_name,
            'session_args': self._session_args,
            'resource_args': self._resource_args
        }

        return config

    # Private methods 
    

    def _get_archive_names(self):
        """
        Returns a list of Archives in the table on Dynamo
        """
        if len(self._table.scan(AttributesToGet=['_id'])['Items']) == 0:
            return []
        else:
            res = [str(archive['_id']) for archive in self._table.scan(
                AttributesToGet=['_id'])['Items']]
            return res

    def _update(self, archive_name, version_metadata):
        '''
        Updates the version specific metadata attribute in DynamoDB
        In DynamoDB this is simply a list append on this attribute value

        Parameters
        ----------
        archive_name: str
            unique '_id' primary key

        version_metadata: dict
            dictionary of version metadata values

        Returns
        -------
        dict
            list of dictionaries of version_metadata
        '''
        self._table.update_item(
            Key={
                '_id': archive_name},
            UpdateExpression="SET version_metadata = list_append(:v, version_metadata)",
            ExpressionAttributeValues={
                ':v': [version_metadata]},
            ReturnValues='ALL_NEW')

    def _get_table_names(self):
        return [t.name for t in self._resource.tables.all()]

    def _create_archive_table(self, table_name):
        if table_name in self._get_table_names():
            raise KeyError('Table "{}" already exists'.format(table_name))

        try:
            self._resource.create_table(TableName=table_name,
                                        KeySchema=[{'AttributeName': '_id',
                                                    'KeyType': 'HASH'},
                                                   ],
                                        AttributeDefinitions=[{'AttributeName': '_id',
                                                               'AttributeType': 'S'},
                                                              ],
                                        ProvisionedThroughput={'ReadCapacityUnits': 123,
                                                               'WriteCapacityUnits': 123})

        except ValueError:
            # Error handling for windows incompatability issue
            assert table_name in self._get_table_names(), 'Table creation failed'

    def _delete_table(self, table_name):
        if table_name not in self._get_table_names():
            raise KeyError('Table "{}" not found'.format(table_name))

        try:

            self._resource.Table(table_name).delete()

        except ValueError:
            # Error handling for windows incompatability issue
            assert table_name not in self._get_table_names(), 'Table deletion failed'

    def _update_metadata(self, archive_name, metadata):
        """
        Appends the updated_metada dict to the Metadata Attribute list

        Parameters
        ----------
        archive_name: str
            Unique GCP_ID archive name

        updated_metadata: dict
            Dictionary of update metadata values
            Right now just lets you append anything to the list

        .. todo::

        """

        # keep the current state in memory
        archive_data_current = self._get_archive_metadata(archive_name)
        archive_data_current.update(metadata)
        # add the updated archive_data object to Dynamo
        updated = self._table.update_item(
            Key={
                '_id': archive_name},
            UpdateExpression="SET archive_data = :v",
            ExpressionAttributeValues={
                ':v': archive_data_current},
            ReturnValues='ALL_NEW')

    def _create_archive(
            self,
            archive_name,
            authority_name,
            service_path,
            metadata):
        '''
        This adds an item in a DynamoDB table corresponding to a S3 object

        Args
        ----
        arhive_name: str
            corresponds to the name of the Archive (e.g. )


        Returns
        -------
        Dictionary with confirmation of upload

        Note
        ----
        versioning is handled by s3

        Todo
        -----
        Coerce underscores to dashes
        '''

        item = {
            '_id': archive_name,
            'authority_name': authority_name,
            'service_path': service_path,
            'version_metadata': [],
            'archive_data': metadata
        }

        if archive_name in self._get_archive_names():

            raise KeyError(
                "{} already exists. Use get_archive() to view".format(archive_name))

        else:
            self._table.put_item(Item=item)

    def _create_if_not_exists(
            self,
            archive_name,
            authority_name,
            service_name,
            metadata):
        try:
            self._create_archive(
                archive_name,
                authority_name,
                service_name,
                metadata)
        except KeyError:
            pass

    def _get_archive_listing(self, archive_name):
        '''
        Return full document for ``{_id:'archive_name'}``

        .. note::

            DynamoDB specific results - do not expose to user
        '''
        return self._table.get_item(Key={'_id': archive_name})['Item']

    def _get_archive_metadata(self, archive_name):

        res = self._get_archive_listing(archive_name)

        return res['archive_data']

    def _get_authority_name(self, archive_name):

        res = self._get_archive_listing(archive_name)

        return res['authority_name']

    def _get_service_path(self, archive_name):

        res = self._get_archive_listing(archive_name)

        return res['service_path']

    def _get_versions(self, archive_name):

        res = self._get_archive_listing(archive_name)

        return res['version_metadata']

    def _get_latest_hash(self, archive_name):

        versions = self._get_versions(archive_name)

        if len(versions) == 0:
            return None

        else:
            return versions[0]['checksum']

    def _delete_archive_record(self, archive_name):

        return self._table.delete_item(Key={'_id': archive_name})
