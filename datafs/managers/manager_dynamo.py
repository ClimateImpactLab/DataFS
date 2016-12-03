import boto3
import botocore.exceptions.ClientError

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

        return [archive['GCP_ID'] for archive in self.table.scan(AttributesToGet=['GCP_ID'])['Items']]

    def _update(self, archive_name, version_id, version_data):
        raise NotImplementedError

    def _update_metadata(self, archive_name, **kwargs):
        raise NotImplementedError

    def _get_services_for_version(self, archive_name, version_id):
        raise NotImplementedError

    def _get_datafile_from_service(self, archive_name, version_id, service):
        raise NotImplementedError

    def _get_all_version_ids(self, archive_name):
        raise NotImplementedError

    def _create_archive(self, archive_name, **metadata):

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
        try:
            res = self.table.put_item(Item={'GCP_ID': archive_name, 'Metadata': metadata})
            assert res['ResponseMetadata']['HTTPStatusCode'] == 200

        except AssertionError:
            return AssertionError

        return res


        

    def _create_if_not_exists(self, archive_name, **metadata):
        raise NotImplementedError

    def _get_archive(self, archive_name):
        raise NotImplementedError
