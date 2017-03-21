
import os
import shutil
import time

from contextlib import contextmanager
from click.testing import CliRunner

from datafs import get_api
from datafs.managers.manager_dynamo import DynamoDBManager
from datafs.managers.manager_mongo import MongoDBManager
from distutils.version import StrictVersion

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

try:
    u = unicode
    string_types = (unicode, str)
except NameError:
    u = str
    string_types = (str,)


def _close(path):

    closed = False

    for i in range(5):
        try:
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)
            closed = True
            break
        except OSError as e:
            time.sleep(0.5)

    if not closed:
        raise e


@contextmanager
def prep_manager(mgr_name, table_name='my-new-data-table'):

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
def setup_runner_resource(config_file, table_name):

    # setup

    runner = CliRunner()

    api = get_api(config_file=config_file)

    prefix = ['--config-file', config_file]

    try:
        api.manager.delete_table(table_name)
    except KeyError:
        pass

    api.manager.create_archive_table(table_name)

    # yield fixture

    yield runner, api, config_file, prefix

    # teardown

    try:
        api.manager.delete_table(table_name)
    except KeyError:
        pass
