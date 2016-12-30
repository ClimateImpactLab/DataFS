
from __future__ import absolute_import
from datafs.managers.manager import BaseDataManager

import pytest

@pytest.fixture
def base_manager():

    mgr = BaseDataManager()
    return mgr



class TestMetadataRequirements(object):

    def test_spec_table_creation(self, manager_with_spec):
        
        assert 'standalone-test-table.spec' in manager_with_spec.table_names

    def test_spec_config_creation(self,manager_with_spec):
    
        assert len(manager_with_spec._get_spec_documents('standalone-test-table')) == 2

    def test_spec_config_update_metadata(self,manager_with_spec):
        assert len(manager_with_spec.required_archive_metadata) == 3

    def test_spec_config_update_user_config(self,manager_with_spec):

        assert len(manager_with_spec.required_user_config) == 3

    def test_manager_spec_setup(self,api_with_spec, auth1):

        metadata_config = {
            'item1': 'test_string1',
            'item2': 'test_string2',
            'item3': 'test_string3'
        }

        user_config = {
            'username': 'My Name',
            'Home Institution': 'Your Institution', 
            'contact': 'my.email@example.com'
            
        }
        
        api_with_spec.user_config.update(user_config)

        api_with_spec.create_archive('my_spec_test_archive', metadata=metadata_config)

        with pytest.raises(AssertionError) as excinfo:
            api_with_spec.create_archive('my_other_test_archive', metadata={})

    def test_manager_spec_setup_api_metadata(self,api_with_spec, auth1):

        metadata_config = {
            'item1': 'test_string1',
            'item2': 'test_string2',
            'item3': 'test_string3'
        }

        with pytest.raises(AssertionError) as excinfo:
            api_with_spec.create_archive('my_api_test_archive', metadata=metadata_config)


class TestBaseManager(object):

    @staticmethod
    def test_update(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._update('archive 1', {})

    @staticmethod
    def test_create_archive(base_manager, auth1):
        with pytest.raises(NotImplementedError):
            base_manager._create_archive(
                'archive_1',
                auth1,
                'archive/1',
                {})

    @staticmethod
    def test_create_if_not_exists(base_manager, auth1):
        with pytest.raises(NotImplementedError):
            base_manager._create_if_not_exists(
                'archive_1',
                auth1,
                'archive/1',
                {})

    @staticmethod
    def test_get_archives(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._get_archives()

    @staticmethod
    def test_get_archive_metadata(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._get_archive_metadata('archive 1')

    @staticmethod
    def test_get_latest_hash(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._get_latest_hash('archive 1')

    @staticmethod
    def test_get_authority_name(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._get_authority_name('archive 1')

    @staticmethod
    def test_get_service_path(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._get_service_path('archive 1')

    @staticmethod
    def test_delete_archive_record(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._delete_archive_record('archive 1')

    @staticmethod
    def test_get_table_names(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._get_table_names()

    @staticmethod
    def test_create_archive_table(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._create_archive_table('my-data-table')

    @staticmethod
    def test_delete_table(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._delete_table('my-data-table')

    @staticmethod
    def test_get_versions(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._get_versions('archive 1')


    def test_update(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._update('archive 1', {})

    def test_create_archive(base_manager, auth1):
        with pytest.raises(NotImplementedError):
            base_manager._create_archive(
                'archive_1',
                auth1,
                'archive/1',
                True,
                {})

    def test_create_if_not_exists(base_manager, auth1):
        with pytest.raises(NotImplementedError):
            base_manager._create_if_not_exists(
                'archive_1',
                auth1,
                'archive/1',
                True,
                {})

    def test_get_archives(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._get_archives()

    def test_get_archive_metadata(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._get_archive_metadata('archive 1')

    def test_get_latest_hash(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._get_latest_hash('archive 1')

    def test_get_authority_name(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._get_authority_name('archive 1')

    def test_get_archive_path(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._get_archive_path('archive 1')

    def test_delete_archive_record(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._delete_archive_record('archive 1')

    def test_get_table_names(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._get_table_names()

    def test_create_archive_table(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._create_archive_table('my-data-table')

    def test_delete_table(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._delete_table('my-data-table')

    def test_get_versions(base_manager):
        with pytest.raises(NotImplementedError):
            base_manager._get_versions('archive 1')
