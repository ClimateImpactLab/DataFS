
from __future__ import absolute_import
from datafs.managers.manager import BaseDataManager
from botocore.exceptions import ClientError
import pytest

@pytest.fixture
def base_manager():

    mgr = BaseDataManager('my-table')
    return mgr



class TestMetadataRequirements:

    def test_spec_table_creation(self, manager_with_spec):
        
        assert 'standalone-test-table.spec' in manager_with_spec.table_names

    def test_spec_config_creation(self,manager_with_spec):
    
        assert len(manager_with_spec._get_spec_documents('standalone-test-table')) == 2

    def test_spec_config_update_metadata(self,manager_with_spec):
        assert len(manager_with_spec.required_archive_metadata) == 1

    def test_spec_config_update_user_config(self,manager_with_spec):

        assert len(manager_with_spec.required_user_config) == 2

    def test_manager_spec_setup(self,api_with_spec, auth1):

        metadata_config = {
            'description': 'test_string1',
        }

        user_config = {
            'username': 'My Name',
            'contact': 'my.email@example.com'
            
        }
        
        api_with_spec.user_config.update(user_config)
        assert api_with_spec.manager.config['table_name'] == 'standalone-test-table'

        api_with_spec.create('my_spec_test_archive', metadata=metadata_config)


        api_with_spec.manager.update_metadata('my_spec_test_archive', {'metadata_key': 'metadata_val'})


        with pytest.raises(ValueError) as excinfo:
            api_with_spec.manager.update_metadata('my_spec_test_archive', dict(description=None))
            

        assert len(api_with_spec.manager.get_metadata('my_spec_test_archive')) == 2
        assert api_with_spec.manager.get_metadata('my_spec_test_archive')['metadata_key'] == 'metadata_val'

        api_with_spec.manager.update_metadata('my_spec_test_archive', {'metadata_key': None})

        assert len(api_with_spec.manager.get_metadata('my_spec_test_archive')) == 1


        assert api_with_spec.manager._get_authority_name('my_spec_test_archive') =='auth'
        assert api_with_spec.manager._get_archive_path('my_spec_test_archive') =='my/spec/test/archive'


        with pytest.raises(AssertionError) as excinfo:
            api_with_spec.create('my_other_test_archive', metadata={'another_string': 'to break the test'})


class TestManagers(object):

    def test_error_handling(self, api):

        with pytest.raises(KeyError) as excinfo:
            api.manager._get_authority_name('nonexistant_archive')

        with pytest.raises(KeyError) as excinfo:
            api.manager._get_archive_path('nonexistant_archive')
        
        with pytest.raises(KeyError) as excinfo:
            api.manager._get_archive_metadata('nonexistant_archive')
        
        with pytest.raises(KeyError) as excinfo:
            api.manager._get_version_history('nonexistant_archive')
        
        with pytest.raises(KeyError) as excinfo:
            api.manager._get_archive_spec('nonexistant_archive')


    def test_table_deletion(self, api):
        
        with pytest.raises(KeyError) as excinfo:
            api.manager._delete_table('nonexistant-table')

        api.manager._delete_table(api.manager._table_name)

        with pytest.raises((KeyError, ClientError)) as excinfo:
            api.manager._update('nonexistant_archive', {})

        api.manager._delete_table(api.manager._spec_table_name)

        with pytest.raises((KeyError, ClientError)) as excinfo:
            api.manager._update_spec_config('required_user_config', {})




    def test_manager_spec_setup_api_metadata(self,api_with_spec, auth1):

        metadata_config = {
            'archive_data': 'test_string1',

        }

        with pytest.raises(AssertionError) as excinfo:
            api_with_spec.create('my_api_test_archive', metadata={})


class TestBaseManager:
    
    def test_update(self, base_manager):
        with pytest.raises(NotImplementedError) as exc_info:
            base_manager._update('archive_name', {})

    def test_create_archive(self, base_manager):
        with pytest.raises(NotImplementedError) as exc_info:
            base_manager._create_archive('archive_name',{})

    def test_create_if_not_exists(self, base_manager):
        with pytest.raises(NotImplementedError) as exc_info:
            base_manager._create_if_not_exists('archive_name', {})

    def test_get_archives(self, base_manager):
        with pytest.raises(NotImplementedError) as exc_info:
            base_manager._get_archives()

    def test_get_archive_metadata(self, base_manager):
        with pytest.raises(NotImplementedError) as exc_info:
            base_manager._get_archive_metadata('archive_name')

    def test_get_latest_hash(self, base_manager):
        with pytest.raises(NotImplementedError) as exc_info:
            base_manager._get_latest_hash('archive_name')

    def test_get_authority_name(self, base_manager):
        with pytest.raises(NotImplementedError) as exc_info:
            base_manager._get_authority_name('archive_name')

    def test_get_archive_path(self, base_manager):
        with pytest.raises(NotImplementedError) as exc_info:
            base_manager._get_archive_path('archive_name')

    def test_delete_archive_record(self, base_manager):
        with pytest.raises(NotImplementedError) as exc_info:
            base_manager._delete_archive_record('archive_name')

    def test_get_table_names(self, base_manager):
        with pytest.raises(NotImplementedError) as exc_info:
            base_manager._get_table_names()

    def test_create_archive_table(self, base_manager):
        with pytest.raises(NotImplementedError) as exc_info:
            base_manager._create_archive_table('table_name')
        
    def test_create_spec_table(self, base_manager):
        with pytest.raises(NotImplementedError) as exc_info:
            base_manager._create_spec_table('table_name')

    def test_create_spec_config(self, base_manager):
        with pytest.raises(NotImplementedError) as exc_info:
            base_manager._create_spec_config('table_name')

    def test_update_spec_config(self, base_manager):
        with pytest.raises(NotImplementedError) as exc_info:
            base_manager._update_spec_config('required_user_config', {})

        with pytest.raises(NotImplementedError) as exc_info:
            base_manager._update_spec_config('required_archive_metadata', {})

    def test_delete_table(self, base_manager):
        with pytest.raises(NotImplementedError) as exc_info:
            base_manager._delete_table('table_name')

    def test_get_required_user_config(self, base_manager):
        with pytest.raises(NotImplementedError) as exc_info:
            base_manager._get_required_user_config()

    def test_get_required_archive_metadata(self, base_manager):
        with pytest.raises(NotImplementedError) as exc_info:
            base_manager._get_required_archive_metadata()

    def test_get_version_history(self, base_manager):
        with pytest.raises(NotImplementedError) as exc_info:
            base_manager._get_version_history('archive_name')
