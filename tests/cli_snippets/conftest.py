from click.testing import CliRunner
from datafs import get_api
from datafs.datafs import cli
from contextlib import contextmanager
import pytest
import os
import itertools

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

    api.manager.delete_table(table_name)


@pytest.yield_fixture(scope='session', params=['mongo', 'dynamo'])
def cli_setup(request, example_snippet_working_dirs):
    config_file = 'examples/snippets/resources/datafs_{}.yml'.format(
                        request.param)

    table_name = 'DataFiles'

    with setup_runner_resource(config_file, table_name) as setup:
        yield setup


@pytest.yield_fixture(scope='session', params=['mongo', 'dynamo'])
def cli_setup_dual_auth(request, example_snippet_working_dirs):
    config_file = 'examples/snippets/resources/datafs_dual_auth_{}.yml'.format(
                        request.param)
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
def cli_validator_and_api(cli_setup, validator):

    _, api, _, prefix = cli_setup

    try:
        api.delete_archive('my_archive')
    except KeyError:
        pass

    validator.call_engines['datafs'] = ClickValidator(app=cli, prefix=prefix)

    yield validator.teststring, api

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


@pytest.yield_fixture(scope='function')
def cli_validator_listdir(cli_setup, validator):

    _, api, _, prefix = cli_setup

    with open('test.txt', 'w') as f:
        f.write('test test')

    tas_archive = api.create('impactlab/climate/tas/tas_daily_us.csv')
    tas_archive.update('test.txt')
    precip_archive = api.create('impactlab/climate/pr/pr_daily_us.csv')
    precip_archive.update('test.txt')
    socio = api.create('impactlab/mortality/global/mortality_global_daily.csv')
    socio.update('test.txt')
    socio1 = api.create('impactlab/conflict/global/conflict_global_daily.csv')
    socio1.update('test.txt')
    socio2 = api.create('impactlab/labor/global/labor_global_daily.csv')
    socio2.update('test.txt')

    validator.call_engines['datafs'] = ClickValidator(app=cli, prefix=prefix)

    yield validator.teststring

    del validator.call_engines['datafs']

    try:
        tas_archive.delete()
        precip_archive.delete()
        socio.delete()
        socio1.delete()
        socio2.delete()
        os.remove('test.txt')
    except KeyError:
        pass


@pytest.yield_fixture(scope='function')
def cli_validator_manager_various(
        cli_setup,
        validator):

    _, api, _, prefix = cli_setup

    archive_names = []
    for indices in itertools.product(*(range(1, 6) for _ in range(3))):
        archive_name = (
            'project{}_variable{}_scenario{}.nc'.format(*indices))
        archive_names.append(archive_name)

    for i, name in enumerate(archive_names):

        if i % 3 == 0:
            try:
                api.create(name, tags=['team1'])
            except KeyError:
                pass

        elif i % 2 == 0:
            try:
                api.create(name, tags=['team2'])
            except KeyError:
                pass
        else:
            try:
                api.create(name, tags=['team3'])
            except KeyError:
                pass

    validator.call_engines['datafs'] = ClickValidator(app=cli, prefix=prefix)

    yield validator.teststring

    del validator.call_engines['datafs']

    # Teardown

    for arch in map(api.get_archive, archive_names):
        arch.delete()
