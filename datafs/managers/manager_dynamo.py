import boto3
#import botocore.exceptions.ClientError

from datafs.managers.manager import BaseDataManager
from datafs.core.data_archive import DataArchive


class DynamoDBManager(BaseDataManager):

    """
    Parameters
    ----------
    api : object
        :py:class:`~datafs.core.data_api.DataAPI` object
    table_name: str
        For Climate Impact Lab table_name = "GCP"

    """

    def __init__(self, table_name, api=None, *args, **kwargs):
        super(DynamoDBManager, self).__init__(api)

        self._session = boto3.Session(profile_name='cil_dynamo')
        self._client = self._session.client('dynamodb', region_name='us-east-1')
        self._resource = self._session.resource('dynamodb',  region_name='us-east-1')
        self.table = self._resource.Table(table_name)



    # Private methods (to be implemented!)
    
    def _get_archives(self):
        """
        Returns a list of Archives in the table on Dynamo


        """


        return [str(archive['GCP_ID']) for archive in self.table.scan(AttributesToGet=['GCP_ID'])['Items']]


    def _update_metadata(self, archive_name, updated_metadata):
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


        self.table.update_item(Key={'GCP_ID': archive_name},
                    UpdateExpression="SET Metadata = list_append(:v, Metadata )",
                    ExpressionAttributeValues={
                    ':v': [updated_metadata]
                    },
                    ReturnValues='ALL_NEW'
                    )

        return self._get_archive(archive_name)['Metadata']



    def _check_if_exists(self, archive_name):
        return self.table.get_item(Key={'GCP_ID':archive_name})['ResponseMetadata']['HTTPHeaders']['x-amz-crc32'] != '2745614147'


    def _create_archive(self, archive_name, authority_name, service_path, **metadata):

        """
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
        """
        #check for existence
        if self._check_if_exists(archive_name):
            print "Archive already exists. Use api.get_archive(archive_name) to retrieve or api.update() to update"

        else:
            try:
                res = self.table.put_item(Item={
                    'GCP_ID': archive_name, 
                    'authority_name': authority_name, 
                    'service_path': service_path, 
                    'Metadata':[metadata]}
                    )
                assert res['ResponseMetadata']['HTTPStatusCode'] == 200

            except AssertionError:
                return AssertionError

            return res
            

        

        

    def _create_if_not_exists(self, archive_name, **metadata):
        self._create_archive(archive_name, **metadata)

    def _get_archive_metadata(self, archive_name):

        return self.table.get_item(Key={'GCP_ID': archive_name})['Item']


    def _update(self, archive_name, version_id, version_data):
        raise NotImplementedError

    def _get_services_for_version(self, archive_name, version_id):
        raise NotImplementedError

    def _get_datafile_from_service(self, archive_name, version_id, service):
        raise NotImplementedError

    def _get_all_version_ids(self, archive_name):
        raise NotImplementedError
        
