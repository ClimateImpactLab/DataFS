
from __future__ import absolute_import
from datafs.managers.manager import BaseDataManager

import pytest

@pytest.fixture
def base_manager():

    mgr = BaseDataManager()
    return mgr


def test_update(base_manager):
    with pytest.raises(NotImplementedError):
        base_manager._update('archive 1', {})

def test_create_archive(base_manager, auth1):
    with pytest.raises(NotImplementedError):
        base_manager._create_archive(
            'archive_1',
            auth1,
            'archive/1',
            {})

def test_create_if_not_exists(base_manager, auth1):
    with pytest.raises(NotImplementedError):
        base_manager._create_if_not_exists(
            'archive_1',
            auth1,
            'archive/1',
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

def test_get_service_path(base_manager):
    with pytest.raises(NotImplementedError):
        base_manager._get_service_path('archive 1')

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
