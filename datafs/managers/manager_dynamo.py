import boto3

from datafs.managers.manager import BaseDataManager
from boto3.dynamodb.conditions import Attr, Key
from functools import reduce


class DynamoDBManager(BaseDataManager):

    """
    Parameters
    ----------
    table_name: str
        Name of the data archive table

    session_args: dict
        Keyword arguments used in initializing a :py:class:`boto3.Session`
        object

    resource_args: dict
        Keyword arguments used in initializing a dynamodb
        :py:class:`~boto3.resources.factory.dynamodb.ServiceResource` object

    """

    def __init__(
            self,
            table_name,
            session_args=None,
            resource_args=None):

        super(DynamoDBManager, self).__init__(table_name)

        self._session_args = {} if session_args is None else session_args
        self._resource_args = {} if resource_args is None else resource_args

        self._session = boto3.Session(**session_args)
        self._resource = self._session.resource('dynamodb', **resource_args)
        self._table = self._resource.Table(self._table_name)
        self._spec_table = self._resource.Table(self._spec_table_name)

    @property
    def config(self):
        config = {
            'table_name': self._table_name,
            'session_args': self._session_args,
            'resource_args': self._resource_args
        }

        return config

    # Private methods

    def _search(self, search_terms, begins_with=None):
        """
        Returns a list of Archive id's in the table on Dynamo

        """

        kwargs = dict(
            ProjectionExpression='#id',
            ExpressionAttributeNames={"#id": "_id"})

        if len(search_terms) > 0:
            kwargs['FilterExpression'] = reduce(
                lambda x, y: x & y,
                [Attr('tags').contains(arg) for arg in search_terms])

        if begins_with:
            if 'FilterExpression' in kwargs:
                kwargs['FilterExpression'] = kwargs[
                    'FilterExpression'] & Key('_id').begins_with(begins_with)

            else:
                kwargs['FilterExpression'] = Key(
                    '_id').begins_with(begins_with)

        while True:
            res = self._table.scan(**kwargs)
            for r in res['Items']:
                yield r['_id']
            if 'LastEvaluatedKey' in res:
                kwargs['ExclusiveStartKey'] = res['LastEvaluatedKey']
            else:
                break

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
            list of dictionaries of version_history
        '''

        command = "SET version_history = list_append(version_history, :v)"

        self._table.update_item(
            Key={'_id': archive_name},
            UpdateExpression=command,
            ExpressionAttributeValues={':v': [version_metadata]},
            ReturnValues='ALL_NEW')

    def _get_table_names(self):
        return [t.name for t in self._resource.tables.all()]

    def _create_archive_table(self, table_name):
        '''
        Dynamo implementation of BaseDataManager create_archive_table

        waiter object is implemented to ensure table creation before moving on
        this will slow down table creation. However, since we are only creating
        table once this should no impact users.

        Parameters
        ----------
        table_name: str

        Returns
        -------
        None

        '''
        if table_name in self._get_table_names():
            raise KeyError('Table "{}" already exists'.format(table_name))

        try:
            table = self._resource.create_table(
                TableName=table_name,
                KeySchema=[{'AttributeName': '_id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[
                    {'AttributeName': '_id', 'AttributeType': 'S'}],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 123,
                    'WriteCapacityUnits': 123})

            table.meta.client.get_waiter('table_exists').wait(
                TableName=table_name)

        except ValueError:
            # Error handling for windows incompatability issue
            msg = 'Table creation failed'
            assert table_name in self._get_table_names(), msg

    def _create_spec_config(self, table_name, spec_documents):
        '''
        Dynamo implementation of spec config creation

        Called by `create_archive_table()` in
        :py:class:`manager.BaseDataManager` Simply adds two rows to the spec
        table

        Parameters
        ----------

        table_name :

            base table name (not including .spec suffix)

        spec_documents : list

            list of dictionary documents defining the manager spec


        '''

        _spec_table = self._resource.Table(table_name + '.spec')

        for doc in spec_documents:
            _spec_table.put_item(Item=doc)

    def _update_spec_config(self, document_name, spec):
        '''
        Dynamo implementation of project specific metadata spec

        '''
        # add the updated archive_metadata object to Dynamo
        self._spec_table.update_item(
            Key={'_id': '{}'.format(document_name)},
            UpdateExpression="SET config = :v",
            ExpressionAttributeValues={':v': spec},
            ReturnValues='ALL_NEW')

    def _delete_table(self, table_name):

        try:
            self._resource.Table(table_name).delete()

        except ValueError:
            # Error handling for windows incompatability issue
            msg = 'Table deletion failed'
            assert table_name not in self._get_table_names(), msg

    def _update_metadata(self, archive_name, archive_metadata):
        """
        Appends the updated_metada dict to the Metadata Attribute list

        Parameters
        ----------
        archive_name: str

            ID of archive to update

        updated_metadata: dict

            dictionary of metadata keys and values to update. If the value
            for a particular key is `None`, the key is removed.

        """

        archive_metadata_current = self._get_archive_metadata(archive_name)
        archive_metadata_current.update(archive_metadata)
        for k, v in archive_metadata_current.items():
            if v is None:
                del archive_metadata_current[k]

        # add the updated archive_metadata object to Dynamo
        self._table.update_item(
            Key={'_id': archive_name},
            UpdateExpression="SET archive_metadata = :v",
            ExpressionAttributeValues={':v': archive_metadata_current},
            ReturnValues='ALL_NEW')

    def _create_archive(
            self,
            archive_name,
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

        '''

        archive_exists = False

        try:
            self.get_archive(archive_name)
            archive_exists = True
        except KeyError:
            pass

        if archive_exists:
            raise KeyError(
                "{} already exists. Use get_archive() to view".format(
                    archive_name))

        self._table.put_item(Item=metadata)

    def _get_archive_listing(self, archive_name):
        '''
        Return full document for ``{_id:'archive_name'}``

        .. note::

            DynamoDB specific results - do not expose to user
        '''
        return self._table.get_item(Key={'_id': archive_name})['Item']

    def _batch_get_archive_listing(self, archive_names):
        '''
        Batched version of :py:meth:`~DynamoDBManager._get_archive_listing`

        Returns a list of full archive listings from an iterable of archive
        names

        .. note ::

            Invalid archive names will simply not be returned, so the response
            may not be the same length as the supplied `archive_names`.

        Parameters
        ----------

        archive_names : list

            List of archive names

        Returns
        -------

        archive_listings : list

            List of archive listings

        '''

        archive_names = list(archive_names)

        MAX_QUERY_LENGTH = 100

        archives = []

        for query_index in range(0, len(archive_names), MAX_QUERY_LENGTH):
            current_query = {
                'Keys': [{'_id': i} for i in archive_names[
                    query_index: query_index+MAX_QUERY_LENGTH]]}

            attempts = 0
            res = {}

            while True:

                if attempts > 0 and len(res.get('UnprocessedKeys', {})) > 0:
                    current_query = res['UnprocessedKeys'][self._table_name]

                elif attempts > 0 and len(res.get('UnprocessedKeys', {})) == 0:
                    break

                res = self._resource.batch_get_item(
                    RequestItems={self._table_name: current_query})

                archives.extend(res['Responses'][self._table_name])

                attempts += 1

        return archives

    def _delete_archive_record(self, archive_name):

        return self._table.delete_item(Key={'_id': archive_name})

    def _get_spec_documents(self, table_name):
        return self._resource.Table(table_name + '.spec').scan()['Items']

    def _set_tags(self, archive_name, updated_tag_list):

        self._table.update_item(
                Key={'_id': archive_name},
                UpdateExpression="SET tags = :t",
                ExpressionAttributeValues={':t': updated_tag_list},
                ReturnValues='ALL_NEW')
