
from __future__ import absolute_import

import pytest

import tempfile
import shutil
import time
import boto
import moto
import os

import fs.utils
from fs.osfs import OSFS
from fs.tempfs import TempFS
from fs.s3fs import S3FS

from datafs import DataAPI
from datafs.core import data_file
from datafs.services.service import DataService
from datafs.managers.manager_mongo import MongoDBManager
from datafs.managers.manager_dynamo import DynamoDBManager

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
            'fs_name', [
                'OSFS', 'S3FS', 'OSFS', 'OSFS', 'S3FS'])

    if 'open_func' in metafunc.fixturenames:
        metafunc.parametrize('open_func', ['open_file', 'get_local_path'])


@contextmanager
def prep_manager(mgr_name):

    table_name = 'my-new-data-table'

    if mgr_name == 'mongo':

        manager_mongo = MongoDBManager(
            database_name='MyDatabase',
            table_name=table_name)

        manager_mongo.create_archive_table(
            table_name,
            raise_on_err=False)

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

        try:
            yield manager_dynamo

        finally:
            manager_dynamo.delete_table(
                table_name,
                raise_on_err=False)

    else:
        raise ValueError('Manager "{}" not recognized'.format(mgr_name))


@contextmanager
def prep_filesystem(fs_name):

    if fs_name == 'OSFS':

        tmpdir = tempfile.mkdtemp()

        try:
            local = OSFS(tmpdir)

            yield local

            local.close()

        finally:
            try:
                shutil.rmtree(tmpdir)
            except (WindowsError, OSError, IOError):
                time.sleep(0.5)
                shutil.rmtree(tmpdir)

    elif fs_name == 'TempFS':

        local = TempFS()

        try:
            yield local

        finally:
            local.close()

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
