from click.testing import CliRunner
from datafs import get_api
from datafs.datafs import cli
from contextlib import contextmanager
import pytest

from fs.tempfs import TempFS

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


@pytest.yield_fixture(scope='function')
def cli_validator(cli_setup):
    
    runner, api, config_file, prefix = cli_setup

    tester = CommandLineTester()
    tester.call_engines['datafs'] = ClickValidator(app=cli, prefix=prefix)
    
    skipped = ['echo', 'cat']

    tester.call_engines.update({
        cmd: SkipValidator() for cmd in skipped})

    yield tester.validate

@pytest.yield_fixture(scope='function')
def cli_validator_with_description(cli_setup):
    
    runner, api, config_file, prefix = cli_setup

    api.manager.set_required_archive_metadata({
        'description': 'Archive description'})

    tester = CommandLineTester()
    tester.call_engines['datafs'] = ClickValidator(app=cli, prefix=prefix)
    
    skipped = ['echo', 'cat']

    tester.call_engines.update({
        cmd: SkipValidator() for cmd in skipped})

    try:
        yield tester.validate

    finally:
        api.manager.set_required_archive_metadata({})


@pytest.yield_fixture(scope='function')
def cli_validator_dual_auth(cli_setup):
    
    runner, api, config_file, prefix = cli_setup

    api.add_authority('my_authority', TempFS())

    tester = CommandLineTester()
    tester.call_engines['datafs'] = ClickValidator(app=cli, prefix=prefix)
    
    skipped = ['echo', 'cat']

    tester.call_engines.update({
        cmd: SkipValidator() for cmd in skipped})

    try:
        yield tester.validate

    finally:
        api.authorities['my_authority'].fs.close()