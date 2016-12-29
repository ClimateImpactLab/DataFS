from contextlib import contextmanager
from datafs.managers.manager_dynamo import DynamoDBManager
from datafs.managers.manager_mongo import MongoDBManager


try:
    u = unicode
    string_types = (unicode, str)
except NameError:
    u = str
    string_types = (str,)



@contextmanager
def prep_manager(mgr_name, table_name = 'my-new-data-table'):
    

    metadata_config = {
        'item1': 'test_string1',
        'item2': 'test_string2',
        'item3': 'test_string3'
    }

    user_config = {
        'Name': 'Your Name',
        'Home Institution': 'Your Institution'
        
    }

    if mgr_name == 'mongo':

        manager_mongo = MongoDBManager(
            database_name='MyDatabase',
            table_name=table_name)

        manager_mongo.create_archive_table(
            table_name,
            raise_on_err=False)

        manager_mongo.update_spec_config('required_metadata_config', metadata_config)
        manager_mongo.update_spec_config('required_user_config', user_config)

        try:
            yield manager_mongo

        finally:
            manager_mongo.delete_table(
                table_name,
                raise_on_err=False)

    elif mgr_name == 'dynamo':

        manager_dynamo = DynamoDBManager(
            table_name,
            session_args={
                'aws_access_key_id': "access-key-id-of-your-choice",
                'aws_secret_access_key': "secret-key-of-your-choice"},
            resource_args={
                'endpoint_url': 'http://localhost:8000/',
                'region_name': 'us-east-1'})

        manager_dynamo.create_archive_table(
            table_name,
            raise_on_err=False)

        manager_dynamo.update_spec_config('required_user_config', user_config)
        manager_dynamo.update_spec_config('required_metadata_config', metadata_config)

        try:
            yield manager_dynamo

        finally:
            manager_dynamo.delete_table(
                table_name,
                raise_on_err=False)

    else:
        raise ValueError('Manager "{}" not recognized'.format(mgr_name))