
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
from tests.resources import prep_manager

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
