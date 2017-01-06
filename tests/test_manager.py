
from __future__ import absolute_import
from datafs.managers.manager import BaseDataManager

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

        api_with_spec.create_archive('my_spec_test_archive', metadata=metadata_config)


        api_with_spec.manager.update_metadata('my_spec_test_archive', {'metadata_key': 'metadata_val'})

        assert len(api_with_spec.manager.get_metadata('my_spec_test_archive')) == 2
        assert api_with_spec.manager.get_metadata('my_spec_test_archive')['metadata_key'] == 'metadata_val'

        api_with_spec.manager.update_metadata('my_spec_test_archive', {'metadata_key': None})

        assert len(api_with_spec.manager.get_metadata('my_spec_test_archive')) == 1


        assert api_with_spec.manager._get_authority_name('my_spec_test_archive') =='auth'
        assert api_with_spec.manager._get_archive_path('my_spec_test_archive') =='my/spec/test/archive'


        with pytest.raises(AssertionError) as excinfo:
            api_with_spec.create_archive('my_other_test_archive', metadata={'another_string': 'to break the test'})



    def test_manager_spec_setup_api_metadata(self,api_with_spec, auth1):

        metadata_config = {
            'archive_data': 'test_string1',

        }

        with pytest.raises(AssertionError) as excinfo:
            api_with_spec.create_archive('my_api_test_archive', metadata={})


class TestBaseManager:
    
    def test_update(self, base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._update('archive 1', {})

    
    def test_create_archive(self, base_manager, auth1):
        with pytest.raises(NotImplementedError):
            base_manager._create_archive(
                'archive_1',
                {})

    
    def test_create_if_not_exists(self, base_manager, auth1):
        with pytest.raises(NotImplementedError):
            base_manager._create_if_not_exists('archive_1', {
                'authority_name': 'auth1',
                'archive_path': 'archive/1'})

    
    def test_get_archives(self, base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._get_archives()

    
    def test_get_archive_metadata(self, base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._get_archive_metadata('archive 1')

    
    def test_get_latest_hash(self, base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._get_latest_hash('archive 1')

    
    def test_get_authority_name(self, base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._get_authority_name('archive 1')

    
    def test_get_archive_path(self, base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._get_archive_path('archive 1')

    
    def test_delete_archive_record(self, base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._delete_archive_record('archive 1')

    
    def test_get_table_names(self, base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._get_table_names()

    
    # def test_create_archive_table(self, api1):
    #     api1.manager._create_archive_table('some_table_name')
    #     assert 'some_table_name' in api1.manager.table_names 
    #     api1.manager._delete_table('some_table_name')
    #     assert 'some_table_name' not in api1.manager.table_names 

    
    def test_delete_table(self, base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._delete_table('my-data-table')

    
    def test_get_version_history(self, base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._get_version_history('archive 1')

