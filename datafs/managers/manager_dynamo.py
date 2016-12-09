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

    def __init__(self, table_name, api=None, session_args={}, resource_args={}):
        super(DynamoDBManager, self).__init__(api)

        self._session = boto3.Session(**session_args)
        self._resource = self._session.resource('dynamodb', **resource_args)
        self.table = self._resource.Table(table_name)

    # Private methods 
    
    def _get_archive_names(self):
        """
        Returns a list of Archives in the table on Dynamo
        """
        if len(self.table.scan()['Items']) == 0:
            return []
        else:
            res = [str(archive['_id']) for archive in self.table.scan(AttributesToGet=['_id'])['Items']]
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
        self.table.update_item(
                    Key={'_id': archive_name},
                    UpdateExpression="SET version_metadata = list_append(:v, version_metadata)",
                    ExpressionAttributeValues={ ':v': [version_metadata]
                    },
                    ReturnValues='ALL_NEW'
                )

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

        #keep the current state in memory
        archive_data_current = self._get_archive_metadata(archive_name)
        archive_data_current.update(metadata)
        #add the updated archive_data object to Dynamo
        updated = self.table.update_item(Key={'_id': archive_name},
                    UpdateExpression="SET archive_data = :v",
                    ExpressionAttributeValues={
                    ':v': archive_data_current
                    },
                    ReturnValues='ALL_NEW'
                    )

    def _create_archive(self, archive_name, authority_name, service_path, metadata):

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
                'version_metadata' : [],
                'archive_data':metadata
                }

        if archive_name in self._get_archive_names():

            raise KeyError("{} already exists. Use get_archive() to view".format(archive_name))
        
        else:
            self.table.put_item(Item=item)

             
    def _create_if_not_exists(self, archive_name, authority_name, service_name, metadata):
        try:
            self._create_archive(archive_name, authority_name, service_name, metadata)
        except KeyError:
            pass

    def _get_archive_listing(self, archive_name):
        '''
        Return full document for ``{_id:'archive_name'}``

        .. note::

            DynamoDB specific results - do not expose to user
        '''
        return self.table.get_item(Key={'_id': archive_name})['Item']

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
        return self.table.delete_item(Key={'_id': archive_name})        