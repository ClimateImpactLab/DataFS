from datafs.datafs import cli
from tests.resources import setup_runner_resource
import pytest

from fs.tempfs import TempFS

from clatter import Runner
from clatter.validators import (
    ClickValidator,
    SubprocessValidator)


@pytest.yield_fixture(scope='session')
def validator():

    tester = Runner()
    tester.call_engines['echo'] = SubprocessValidator()
    tester.call_engines['cat'] = SubprocessValidator()
    tester.call_engines['python'] = SubprocessValidator()

    yield tester


@pytest.yield_fixture(scope='session')
def cli_setup(example_snippet_working_dirs):
    config_file = 'examples/snippets/resources/datafs.yml'
    table_name = 'DataFiles'

    with setup_runner_resource(config_file, table_name) as setup:
        yield setup


@pytest.yield_fixture(scope='session')
def cli_setup_dual_auth(example_snippet_working_dirs):
    config_file = 'examples/snippets/resources/datafs_dual_auth.yml'
    table_name = 'OtherFiles'

    with setup_runner_resource(config_file, table_name) as setup:
        yield setup


@pytest.yield_fixture(scope='function')
def cli_validator(cli_setup, validator):

    _, api, _, prefix = cli_setup

    try:
        api.delete_archive('my_archive')
    except KeyError:
        pass

    validator.call_engines['datafs'] = ClickValidator(app=cli, prefix=prefix)

    yield validator.teststring

    del validator.call_engines['datafs']


@pytest.yield_fixture(scope='function')
def cli_validator_with_description(cli_setup, cli_validator):

    _, api, _, _ = cli_setup

    api.manager.set_required_archive_metadata({
        'description': 'Archive description'})

    try:
        yield cli_validator

    finally:
        api.manager.set_required_archive_metadata({})


@pytest.yield_fixture(scope='function')
def cli_validator_dual_auth(cli_setup_dual_auth, validator):

    _, api, _, prefix = cli_setup_dual_auth

    try:
        api.delete_archive('my_archive')
    except KeyError:
        pass

    validator.call_engines['datafs'] = ClickValidator(app=cli, prefix=prefix)

    api.attach_authority('my_authority', TempFS())

    try:
        yield validator.teststring

    finally:
        api._authorities['my_authority'].fs.close()
        del validator.call_engines['datafs']
