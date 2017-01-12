
from __future__ import absolute_import

import pytest

import tempfile
import shutil
import time
import boto
import moto
import os
import itertools

import fs1.utils
from fs1.osfs import OSFS
from fs1.tempfs import TempFS
from fs1.s3fs import S3FS

from datafs import DataAPI
from datafs._compat import string_types
from datafs.core import data_file
from datafs.services.service import DataService
from datafs.managers.manager import BaseDataManager
from datafs.managers.manager_mongo import MongoDBManager
from datafs.managers.manager_dynamo import DynamoDBManager
from tests.resources import prep_manager, _close

from contextlib import contextmanager




def pytest_generate_tests(metafunc):
    '''
    Build an API connection for use in testing
    '''

    if 'mgr_name' in metafunc.fixturenames:

        metafunc.parametrize('mgr_name', ['mongo', 'dynamo'])
        # metafunc.parametrize('mgr_name', ['mongo'])

    if 'fs_name' in metafunc.fixturenames:

        metafunc.parametrize(
            'fs_name', ['OSFS', 'S3FS'])

    if 'open_func' in metafunc.fixturenames:
        metafunc.parametrize('open_func', ['open_file', 'get_local_path'])


@pytest.yield_fixture
def tempdir():
    tmpdir = tempfile.mkdtemp()

    try:
        yield tmpdir

    finally:
        _close(tmpdir)

@contextmanager
def prep_filesystem(fs_name):

    if fs_name == 'OSFS':

        tmpdir = tempfile.mkdtemp()

        try:
            local = OSFS(tmpdir)

            yield local

            local.close()

        finally:
            _close(tmpdir)

    elif fs_name == 'S3FS':

        m = moto.mock_s3()
        m.start()

        try:

            s3 = S3FS(
                'test-bucket',
                aws_access_key='MY_KEY',
                aws_secret_key='MY_SECRET_KEY')

            yield s3
            s3.close()

        finally:
            m.stop()




@pytest.yield_fixture
def api(mgr_name, fs_name):

    with prep_manager(mgr_name) as manager:

        api = DataAPI(
            username='My Name',
            contact='my.email@example.com')

        api.attach_manager(manager)

        with prep_filesystem(fs_name) as filesystem:
            api.attach_authority('filesys', filesystem)

            yield api


@pytest.yield_fixture
def api1(mgr_name):

    with prep_manager(mgr_name) as manager:

        api = DataAPI(
            username='My Name',
            contact='my.email@example.com')

        api.attach_manager(manager)

        yield api


@pytest.yield_fixture
def api2(mgr_name):

    with prep_manager(mgr_name) as manager:

        api = DataAPI(
            username='My Name',
            contact='my.email@example.com')

        api.attach_manager(manager)

        yield api


@pytest.yield_fixture(scope='function')
def local_auth():

    with prep_filesystem('OSFS') as filesystem:
        yield filesystem


@pytest.yield_fixture(scope='function')
def auth1(fs_name):

    with prep_filesystem(fs_name) as filesystem:
        yield filesystem


@pytest.yield_fixture(scope='function')
def auth2(fs_name):

    with prep_filesystem(fs_name) as filesystem:
        yield filesystem


@pytest.yield_fixture(scope='function')
def cache():

    with prep_filesystem('OSFS') as filesystem:
        yield filesystem


@pytest.yield_fixture(scope='function')
def cache1():

    with prep_filesystem('OSFS') as filesystem:
        yield filesystem


@pytest.yield_fixture(scope='function')
def cache2():

    with prep_filesystem('OSFS') as filesystem:
        yield filesystem


@pytest.yield_fixture
def manager_with_spec(mgr_name):

    with prep_manager(mgr_name, table_name='standalone-test-table') as manager:


        metadata_config = {
            'description': 'some metadata'
            }

        user_config = {
            'username': 'Your Name',
            'contact': 'my.email@example.com'
            
        }


        manager.set_required_user_config(user_config)
        manager.set_required_archive_metadata(metadata_config)

        manager.required_user_config
        manager.required_archive_metadata

        yield manager


@pytest.yield_fixture
def api_with_spec(manager_with_spec, auth1):

        api = DataAPI(
            username='My Name',
            contact='my.email@example.com')

        api.attach_manager(manager_with_spec)
        api.attach_authority('auth', auth1)

        yield api


@pytest.fixture
def opener(open_func):
    '''
    Fixture for opening files using each of the available methods

    open_func is parameterized in conftest.py
    '''

    if open_func == 'open_file':

        @contextmanager
        def inner(
            archive, 
            mode='r', 
            version=None, 
            bumpversion='patch', 
            prerelease=None, 
            dependencies=None,
            *args, 
            **kwargs):

            with archive.open(
                *args, 
                mode=mode,
                version=version, 
                bumpversion=bumpversion, 
                prerelease=prerelease,
                dependencies=dependencies, 
                **kwargs) as f:
                
                yield f

        return inner

    elif open_func == 'get_local_path':

        @contextmanager
        def inner(
            archive, 
            mode='r', 
            version=None, 
            bumpversion='patch', 
            prerelease=None, 
            dependencies=None,
            *args, 
            **kwargs):

            with archive.get_local_path(
                version=version, 
                bumpversion=bumpversion, 
                prerelease=prerelease,
                dependencies=dependencies) as fp:
                
                with open(fp, mode=mode, *args, **kwargs) as f:
                    yield f

        return inner

    else:
        raise NameError('open_func "{}" not recognized'.format(open_func))



@pytest.fixture
def datafile_opener(open_func):
    '''
    Fixture for opening files using each of the available methods

    open_func is parameterized in conftest.py
    '''

    if open_func == 'open_file':

        return data_file.open_file

    elif open_func == 'get_local_path':

        @contextmanager
        def inner(
                auth,
                cache,
                update,
                version_check,
                hasher,
                read_path,
                write_path=None,
                cache_on_write=False,
                *args,
                **kwargs):

            with data_file.get_local_path(
                auth, 
                cache, 
                update, 
                version_check, 
                hasher, 
                read_path, 
                write_path, 
                cache_on_write) as fp:

                assert isinstance(fp, string_types)

                with open(fp, *args, **kwargs) as f:
                    yield f

        return inner

    else:
        raise NameError('open_func "{}" not recognized'.format(open_func))




@pytest.yield_fixture
def api_with_diverse_archives(mgr_name, fs_name):

    with prep_manager(mgr_name) as manager:

        api = DataAPI(
            username='My Name',
            contact='my.email@example.com')

        api.attach_manager(manager)

        with prep_filesystem(fs_name) as auth:

            api.attach_authority('auth', auth1)

            for indices in itertools.product(*(range(1,4) for _ in range(5))):
                api.create(
                    'team{}_project{}_task{}_variable{}_scenario{}.nc'.format(
                        *indices))


            for indices in itertools.product(*(range(1,4) for _ in range(5))):
                api.create(
                    'team{}_project{}_task{}_parameter{}_scenario{}.csv'.format(
                        *indices))


            for indices in itertools.product(*(range(1,4) for _ in range(3))):
                api.create(
                    'team{}_project{}_task{}_config.txt'.format(
                        *indices))

            api.TEST_ATTRS = {
                'archives.variable': 243,
                'archives.parameter': 243,
                'archives.config': 27,
                'count.variable': 3,
                'count.parameter': 3,
                'count.config': 1
            }


            yield api