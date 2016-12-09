
from __future__ import absolute_import

import doctest
import datafs
import moto
from examples import (local, ondisk, s3, caching)
from examples.subclassing import client
from datafs.managers.manager_dynamo import DynamoDBManager

def test_local():
    doctest.testmod(local, raise_on_error=True)


def test_ondisk():

    has_special_dependencies = False

    try:
        import netCDF4
        import xarray as xr
        has_special_dependencies = True

    except ImportError:
        pass

    if has_special_dependencies:
        doctest.testmod(ondisk, raise_on_error=True)


def test_s3():

    m = moto.mock_s3()
    m.start()

    try:
        doctest.testmod(s3, raise_on_error=True)

    finally:
        # Stop mock
        m.stop()


def test_caching():
    doctest.testmod(caching, raise_on_error=True)


def test_subclassing():

    table_name = 'project_data'
    manager = DynamoDBManager(
        table_name, 
        session_args={
            'aws_access_key_id': "access-key-id-of-your-choice",
            'aws_secret_access_key': "secret-key-of-your-choice"}, 
        resource_args={
            'endpoint_url':'http://localhost:8000/',
            'region_name':'us-east-1'})

    if table_name in manager.table_names:
        manager.delete_table(table_name)

    manager.create_archive_table(table_name, raise_if_exists=False)
        
    doctest.testmod(client, raise_on_error=True)

    manager.delete_table(table_name)

