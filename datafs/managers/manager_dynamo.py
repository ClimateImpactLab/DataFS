
import boto3
#import botocore.exceptions.ClientError

from datafs.managers.manager import BaseDataManager


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
            session_args={},
            resource_args={}):

        super(DynamoDBManager, self).__init__(table_name)

        self._session_args = session_args
        self._resource_args = resource_args

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
            list of dictionaries of version_history
        '''
        self._table.update_item(
            Key={
                '_id': archive_name},
            UpdateExpression="SET version_history = list_append(version_history, :v)",
            ExpressionAttributeValues={
                ':v': [version_metadata]},
            ReturnValues='ALL_NEW')

    def _get_table_names(self):
        return [t.name for t in self._resource.tables.all()]

    def _create_archive_table(self, table_name):
        '''
        Dynamo implementation of BaseDataManager create_archive_table

        waiter object is implemented to ensure table creation before moving on
        this will slow down table creation. However, since we are only creating table once
        this should no impact users. 

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
            table = self._resource.create_table(TableName=table_name,
                                        KeySchema=[{'AttributeName': '_id',
                                                    'KeyType': 'HASH'},
                                                   ],
                                        AttributeDefinitions=[{'AttributeName': '_id',
                                                               'AttributeType': 'S'},
                                                              ],
                                        ProvisionedThroughput={'ReadCapacityUnits': 123,
                                                               'WriteCapacityUnits': 123})
            table.meta.client.get_waiter('table_exists').wait(TableName=table_name)


        except ValueError:
            # Error handling for windows incompatability issue
            assert table_name in self._get_table_names(), 'Table creation failed'


    def _create_spec_table(self, table_name):
        '''
        Dynamo implementation of User and Metadata Spec configuration
        Called by `create_archive_table()` in :py:class:`manager.BaseDataManager`. 
        This table will additional table will be aliased by 'table_name.spec'

        A waiter is implemented on Dynamo to ensure table exists before executing any subsequent operations

        Paramters
        ---------
        table_name: str

        Returns
        -------
        None
        '''

        spec_table = table_name + '.spec'
        

        if spec_table in self._get_table_names():
            raise KeyError('Table "{}" already exists'.format(spec_table))

        try:
            table = self._resource.create_table(
                TableName=spec_table,
                KeySchema=[
                    {'AttributeName': '_id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[
                    {'AttributeName': '_id','AttributeType': 'S'}],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 123,'WriteCapacityUnits': 123})

            table.meta.client.get_waiter('table_exists').wait(TableName=spec_table)


        except ValueError:
            # Error handling for windows incompatability issue
            assert spec_table in self._get_table_names(), 'Table creation failed'

    def _create_spec_config(self, table_name):
        '''
        Dynamo implementation of spec config creation
        Called by `create_archive_table()` in :py:class:`manager.BaseDataManager`
        Simply adds two rows to the spec table

        Parameters
        ----------
        table_name

        Returns
        -------
        None

        '''

        _spec_table = self._resource.Table(table_name + '.spec')

        user_config = {
            '_id': 'required_user_config',
            'config': {}
        }

        archive_config = {
            '_id': 'required_archive_metadata',
            'config': {}
        }

        

        _spec_table.put_item(Item=user_config)
        _spec_table.put_item(Item=archive_config)


    def _update_spec_config(self, document_name, spec={}):
        '''
        Dynamo implementation of project specific metadata spec

        
        '''


        
        
        spec_data_current  = self._spec_table.get_item(
                                Key={'_id': '{}'.format(document_name)})['Item']['config']

        #print(spec_data_current)
        # keep the current state in memory
        
        spec_data_current.update(spec)
        #print(spec_data_current)
        # add the updated archive_metadata object to Dynamo
        updated = self._spec_table.update_item(
            Key={
                '_id': '{}'.format(document_name)},
            UpdateExpression="SET config = :v",
            ExpressionAttributeValues={
                ':v': spec_data_current},
            ReturnValues='ALL_NEW')



    def _delete_table(self, table_name):
        if table_name not in self._get_table_names():
            raise KeyError('Table "{}" not found'.format(table_name))

        try:
            self._resource.Table(table_name).delete()

        except ValueError:
            # Error handling for windows incompatability issue
            assert table_name not in self._get_table_names(), 'Table deletion failed'

    def _update_metadata(self, archive_name, archive_metadata):
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
        required_metadata_keys= self._get_required_archive_metadata().keys()
        for k,v in archive_metadata.items(): 
            if k in required_metadata_keys and v is None:
                raise ValueError('Value for key {} is None. None cannot be a value for required metadata'.format(k))



        archive_metadata_current = self._get_archive_metadata(archive_name)
        archive_metadata_current.update(archive_metadata)
        for k, v in archive_metadata_current.items():
            if v is None:
                del archive_metadata_current[k]

        # add the updated archive_metadata object to Dynamo
        updated = self._table.update_item(
            Key={
                '_id': archive_name},
            UpdateExpression="SET archive_metadata = :v",
            ExpressionAttributeValues={
                ':v': archive_metadata_current},
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

        Note
        ----
        versioning is handled by s3

        Todo
        -----
        Coerce underscores to dashes
        '''


        if archive_name in self._get_archive_names():

            raise KeyError(
                "{} already exists. Use get_archive() to view".format(archive_name))

        else:
            self._table.put_item(Item=metadata)

    def _create_if_not_exists(
            self,
            archive_name,
            metadata):
        try:
            self._create_archive(
                archive_name,
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

        return res['archive_metadata']

    def _get_archive_spec(self, archive_name):
        res = self._get_archive_listing(archive_name)

        if res is None:
            raise KeyError

        spec = ['authority_name', 'archive_path', 'versioned']

        return {k:v for k,v in res.items() if k in spec}

    def _get_authority_name(self, archive_name):

        res = self._get_archive_listing(archive_name)

        return res['authority_name']

    def _get_archive_path(self, archive_name):

        res = self._get_archive_listing(archive_name)

        return res['archive_path']

    def _get_version_history(self, archive_name):

        res = self._get_archive_listing(archive_name)

        return res['version_history']

    def _get_latest_hash(self, archive_name):

        version_history = self._get_version_history(archive_name)

        if len(version_history) == 0:
            return None

        else:
            return version_history[-1]['checksum']

    def _get_required_user_config(self):



        return self._spec_table.get_item(Key={
                            '_id': '{}'.format('required_user_config')})['Item']['config']


    def _get_required_archive_metadata(self):

        return self._spec_table.get_item(Key={
                            '_id': '{}'.format('required_archive_metadata')})['Item']['config']


    def _delete_archive_record(self, archive_name):

        return self._table.delete_item(Key={'_id': archive_name})


    def _get_spec_documents(self, table_name):
        return self._resource.Table(table_name + '.spec').scan()['Items']



