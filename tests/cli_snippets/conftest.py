
from click.testing import CliRunner
from datafs import get_api
from contextlib import contextmanager
import pytest


@contextmanager
def setup_runner_resource(config_file, table_name, archive_name):

    # setup

    runner = CliRunner()

    api = get_api(config_file=config_file)

    prefix = ['--config-file', config_file]

    try:
        api.delete_archive(archive_name)
    except:
        pass

    try:
        api.manager.delete_table(table_name)
    except:
        pass

    api.manager.create_archive_table(table_name)

    # yield fixture

    yield runner, api, config_file, prefix

    # teardown

    api.manager.delete_table(table_name)


@pytest.yield_fixture(scope='function')
def cli_setup():
    config_file = 'examples/snippets/resources/datafs.yml'
    table_name = 'DataFiles'
    archive_name = 'my_archive'

    with setup_runner_resource(config_file, table_name, archive_name) as setup:
        yield setup


@pytest.yield_fixture(scope='function')
def cli_setup_dual_auth():
    config_file = 'examples/snippets/resources/datafs_dual_auth.yml'
    table_name = 'OtherFiles'
    archive_name = 'my_archive'

    with setup_runner_resource(config_file, table_name, archive_name) as setup:
        yield setup
