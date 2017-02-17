
from __future__ import absolute_import
from datafs.managers.manager import BaseDataManager
from botocore.exceptions import ClientError
import pytest


@pytest.fixture
def base_manager():

    mgr = BaseDataManager('my-table')
    return mgr


def test_spec_table_creation(manager_with_spec):

    assert 'spec-test.spec' in manager_with_spec.table_names


def test_spec_config_creation(manager_with_spec):

    assert len(manager_with_spec._get_spec_documents(
        'spec-test')) == 3


def test_spec_config_update_metadata(manager_with_spec):
    assert len(manager_with_spec.required_archive_metadata) == 1


def test_spec_config_update_user_config(manager_with_spec):

    assert len(manager_with_spec.required_user_config) == 2


def test_manager_spec_setup(api_with_spec, auth1):

    metadata_config = {
        'description': 'test_string1',
    }

    user_config = {
        'username': 'My Name',
        'contact': 'my.email@example.com'

    }

    api_with_spec.user_config.update(user_config)
    assert api_with_spec.manager.config[
        'table_name'] == 'spec-test'

    api_with_spec.create('my_spec_test_archive', metadata=metadata_config)

    api_with_spec.manager.update_metadata(
        'my_spec_test_archive', {
            'metadata_key': 'metadata_val'})

    with pytest.raises(ValueError):
        api_with_spec.manager.update_metadata(
            'my_spec_test_archive', dict(description=None))

    assert len(api_with_spec.manager.get_metadata(
        'my_spec_test_archive')) == 2
    assert api_with_spec.manager.get_metadata('my_spec_test_archive')[
        'metadata_key'] == 'metadata_val'

    api_with_spec.manager.update_metadata(
        'my_spec_test_archive', {'metadata_key': None})

    assert len(api_with_spec.manager.get_metadata(
        'my_spec_test_archive')) == 1

    assert api_with_spec.manager._get_authority_name(
        'my_spec_test_archive') == 'auth'
    assert api_with_spec.manager._get_archive_path(
        'my_spec_test_archive') == 'my_spec_test_archive'

    with pytest.raises(AssertionError):
        api_with_spec.create(
            'my_other_test_archive', metadata={
                'another_string': 'to break the test'})


def test_error_handling(api):

    with pytest.raises(KeyError):
        api.manager._get_authority_name('nonexistant_archive')

    with pytest.raises(KeyError):
        api.manager._get_archive_path('nonexistant_archive')

    with pytest.raises(KeyError):
        api.manager._get_archive_metadata('nonexistant_archive')

    with pytest.raises(KeyError):
        api.manager._get_version_history('nonexistant_archive')

    with pytest.raises(KeyError):
        api.manager._get_archive_spec('nonexistant_archive')


def test_table_deletion(api):

    with pytest.raises(KeyError):
        api.manager.delete_table('nonexistant-table')

    api.manager.delete_table(api.manager._table_name)

    with pytest.raises((KeyError, ClientError)):
        api.manager._update('nonexistant_archive', {})

    with pytest.raises((KeyError, ClientError)):
        api.manager._update_spec_config('required_user_config', {})


def test_manager_spec_setup_api_metadata(api_with_spec, auth1):

    with pytest.raises(AssertionError):
        api_with_spec.create('my_api_test_archive', metadata={})


def test_base_manager_update(base_manager):
    with pytest.raises(NotImplementedError):
        base_manager._update('archive_name', {})


def test_base_manager_create_archive(base_manager):
    with pytest.raises(NotImplementedError):
        base_manager._create_archive('archive_name', {})


def test_base_manager_create_if_not_exists(base_manager):
    with pytest.raises(NotImplementedError):
        base_manager._create_if_not_exists('archive_name', {})


def test_base_manager_get_archives(base_manager):
    with pytest.raises(NotImplementedError):
        base_manager._get_archives()


def test_base_manager_get_archive_listing(base_manager):
    with pytest.raises(NotImplementedError):
        base_manager._get_archive_listing('archive_name')


def test_base_manager_get_archive_metadata(base_manager):
    with pytest.raises(NotImplementedError):
        base_manager._get_archive_metadata('archive_name')


def test_base_manager_get_latest_base_manager_hash(base_manager):
    with pytest.raises(NotImplementedError):
        base_manager._get_latest_hash('archive_name')


def test_base_manager_get_authority_name(base_manager):
    with pytest.raises(NotImplementedError):
        base_manager._get_authority_name('archive_name')


def test_base_manager_get_archive_path(base_manager):
    with pytest.raises(NotImplementedError):
        base_manager._get_archive_path('archive_name')


def test_base_manager_delete_archive_record(base_manager):
    with pytest.raises(NotImplementedError):
        base_manager._delete_archive_record('archive_name')


def test_base_manager_get_table_names(base_manager):
    with pytest.raises(NotImplementedError):
        base_manager._get_table_names()


def test_base_manager_create_archive_table(base_manager):
    with pytest.raises(NotImplementedError):
        base_manager._create_archive_table('table_name')


def test_base_manager_create_spec_config(base_manager):
    with pytest.raises(NotImplementedError):
        base_manager._create_spec_config('table_name', [{}, {}, {}])


def test_base_manager_update_spec_config(base_manager):
    with pytest.raises(NotImplementedError):
        base_manager._update_spec_config('required_user_config', {})

    with pytest.raises(NotImplementedError):
        base_manager._update_spec_config('required_archive_metadata', {})


def test_base_manager_delete_table(base_manager):
    with pytest.raises(NotImplementedError):
        base_manager._delete_table('table_name')


def test_base_manager_get_version_history(base_manager):
    with pytest.raises(NotImplementedError):
        base_manager._get_version_history('archive_name')


def test_base_manager_search(base_manager):
    with pytest.raises(NotImplementedError):
        base_manager._search('archive_name', ['term1', 'term2'])


def test_base_manager_set_tags(base_manager):
    with pytest.raises(NotImplementedError):
        base_manager._set_tags('archive_name', ['term1', 'term2'])
