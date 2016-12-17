
from __future__ import absolute_import

import doctest
import datafs
import moto
from examples import (local, ondisk, s3, caching)
from examples.subclassing import client
from datafs.managers.manager_dynamo import DynamoDBManager


def mock_s3(func):
    def inner(*args, **kwargs):

        m = moto.mock_s3()
        m.start()

        try:
            return func(*args, **kwargs)

        finally:
            m.stop()

    return inner


def test_local():
    failures, tests = doctest.testmod(local, report=True)
    assert failures == 0


@mock_s3
def test_ondisk():

    has_special_dependencies = False

    try:
        import netCDF4
        import xarray as xr
        has_special_dependencies = True

    except ImportError:
        pass

    if has_special_dependencies:
        failures, tests = doctest.testmod(ondisk, report=True)
        assert failures == 0


@mock_s3
def test_s3():

    failures, tests = doctest.testmod(s3, report=True)
    assert failures == 0


@mock_s3
def test_caching():

    failures, tests = doctest.testmod(caching, report=True)
    assert failures == 0


def test_subclassing():

    table_name = 'project_data'
    manager = DynamoDBManager(
        table_name,
        session_args={
            'aws_access_key_id': "access-key-id-of-your-choice",
            'aws_secret_access_key': "secret-key-of-your-choice"},
        resource_args={
            'endpoint_url': 'http://localhost:8000/',
            'region_name': 'us-east-1'})

    manager.delete_table(table_name, raise_on_err=False)

    manager.create_archive_table(table_name, raise_on_err=False)

    failures, tests = doctest.testmod(client, report=True)
    assert failures == 0

    manager.delete_table(table_name)
