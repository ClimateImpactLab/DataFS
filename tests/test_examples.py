
from __future__ import absolute_import

import pytest
import doctest
import moto
from examples import (local, ondisk, s3, caching)
from examples.preconfigured import preconfigured
from examples.subclassing import client
from examples.snippets import (
    pythonapi_creating_archives,
    pythonapi_dependencies,
    pythonapi_io,
    pythonapi_metadata,
    pythonapi_versioning)
from datafs.managers.manager_dynamo import DynamoDBManager
from distutils.version import StrictVersion


@pytest.mark.examples
def mock_s3(func):
    def inner(*args, **kwargs):

        m = moto.mock_s3()
        m.start()

        try:
            return func(*args, **kwargs)

        finally:
            m.stop()

    return inner


@pytest.mark.examples
def test_local():
    failures, _ = doctest.testmod(local, report=True)
    assert failures == 0


@pytest.mark.examples
@mock_s3
def test_ondisk():

    has_special_dependencies = False

    try:
        import netCDF4
        assert StrictVersion(netCDF4.__version__) >= '1.1'

        import numpy as np
        assert StrictVersion(np.__version__) >= '1.7'

        import pandas as pd
        assert StrictVersion(pd.__version__) >= '0.15'

        import xarray as xr
        assert StrictVersion(xr.__version__) >= '0.8'

        has_special_dependencies = True

    except (ImportError, AssertionError):
        pass

    if has_special_dependencies:
        failures, _ = doctest.testmod(ondisk, report=True)
        assert failures == 0


@pytest.mark.examples
@mock_s3
def test_s3():

    failures, _ = doctest.testmod(s3, report=True)
    assert failures == 0


@pytest.mark.examples
@mock_s3
def test_caching():

    failures, _ = doctest.testmod(caching, report=True)
    assert failures == 0


@pytest.mark.examples
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

    failures, _ = doctest.testmod(client, report=True)
    assert failures == 0

    manager.delete_table(table_name)


@pytest.mark.examples
def test_preconfigured():
    failures, _ = doctest.testmod(preconfigured, report=True)
    assert failures == 0


@pytest.mark.examples
def test_docs_pythonapi_creating_archives():
    failures, _ = doctest.testmod(pythonapi_creating_archives, report=True)
    assert failures == 0


@pytest.mark.examples
def test_docs_pythonapi_dependencies():
    failures, _ = doctest.testmod(pythonapi_dependencies, report=True)
    assert failures == 0


@pytest.mark.examples
def test_docs_pythonapi_io():
    failures, _ = doctest.testmod(pythonapi_io, report=True)
    assert failures == 0


@pytest.mark.examples
def test_docs_pythonapi_metadata():
    failures, _ = doctest.testmod(pythonapi_metadata, report=True)
    assert failures == 0


@pytest.mark.examples
def test_docs_pythonapi_versioning():
    failures, _ = doctest.testmod(pythonapi_versioning, report=True)
    assert failures == 0
