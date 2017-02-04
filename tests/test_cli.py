from datafs.managers.manager_dynamo import DynamoDBManager
from datafs.datafs import cli
from datafs import DataAPI, get_api, to_config_file
import os
from click.testing import CliRunner
import pytest
import ast


@pytest.yield_fixture(scope='module')
def manager_table():

    # setup manager table

    table_name = 'my-cli-test-table'

    manager = DynamoDBManager(
        table_name,
        session_args={
            'aws_access_key_id': "access-key-id-of-your-choice",
            'aws_secret_access_key': "secret-key-of-your-choice"},
        resource_args={
            'endpoint_url': 'http://localhost:8000/',
            'region_name': 'us-east-1'})

    manager.create_archive_table(table_name, raise_on_err=False)

    try:
        yield table_name

    finally:
        manager.delete_table(table_name)


@pytest.yield_fixture(scope='module')
def test_config(manager_table, temp_dir_mod, temp_file):
    my_test_yaml = r'''
default-profile: myapi
profiles:
  myapi:
    api:
      user_config:
        username: 'My Name'
        contact: 'my.email@example.com'
    authorities:
      local:
        args:
          - "{dir}"
        service: OSFS
    manager:
      class: "DynamoDBManager"
      kwargs:
        resource_args:
            endpoint_url: "http://localhost:8000/"
            region_name: "us-east-1"
        session_args:
            aws_access_key_id: "access-key-id-of-your-choice"
            aws_secret_access_key: "secret-key-of-your-choice"
        table_name: "{table}"
'''.format(table=manager_table, dir=temp_dir_mod)

    with open(temp_file, 'w+') as f:
        f.write(my_test_yaml)

    yield 'myapi', temp_file


@pytest.yield_fixture(scope='module')
def preloaded_config(test_config):
    '''
    Prepare a manager/auth config with 3 archives, each having 3 versions

    .. note::

        To save on test runtime, scope == module. Tests should not modify
        these archives.

    '''

    profile, temp_file = test_config

    api = get_api(profile=profile, config_file=temp_file)

    # Set up a couple archives with multiple versions

    arch1 = api.create('req_1')
    arch2 = api.create('req_2')
    arch3 = api.create('req_3')

    with arch1.open('w+', bumpversion='minor') as f:
        f.write(u'this is archive req_1 version 0.1')

    with arch1.open('w+', bumpversion='major') as f:
        f.write(u'this is archive req_1 version 1.0')

    with arch1.open('w+', bumpversion='minor') as f:
        f.write(u'this is archive req_1 version 1.1')

    arch1_versions = arch1.get_versions()
    assert '0.1' in arch1_versions
    assert '1.0' in arch1_versions
    assert '1.1' in arch1_versions

    with arch2.open('w+', prerelease='alpha') as f:
        f.write(u'this is archive req_2 version 0.0.1a1')

    with arch2.open('w+', prerelease='alpha') as f:
        f.write(u'this is archive req_2 version 0.0.1a2')

    with arch2.open('w+', bumpversion='patch') as f:
        f.write(u'this is archive req_2 version 0.0.1')

    arch2_versions = arch2.get_versions()
    assert '0.0.1a1' in arch2_versions
    assert '0.0.1a2' in arch2_versions
    assert '0.0.1' in arch2_versions

    with arch3.open('w+', bumpversion='major') as f:
        f.write(u'this is archive req_3 version 1.0')

    with arch3.open('w+', bumpversion='minor', prerelease='alpha') as f:
        f.write(u'this is archive req_3 version 1.1a1')

    with arch3.open('w+', bumpversion='minor') as f:
        f.write(u'this is archive req_3 version 1.1')

    arch3_versions = arch3.get_versions()
    assert '1.0' in arch3_versions
    assert '1.1a1' in arch3_versions
    assert '1.1' in arch3_versions

    try:

        yield profile, temp_file

    finally:

        arch1.delete()
        arch2.delete()
        arch3.delete()


def test_cli_local(test_config):

    profile, temp_file = test_config

    prefix = ['--config-file', temp_file, '--profile', 'myapi']

    api2 = get_api(profile=profile, config_file=temp_file)

    runner = CliRunner()

    # test for configure and create archive
    result = runner.invoke(cli,
                           prefix + ['create',
                                     'my_first_archive',
                                     '--description',
                                     'My test data archive'])

    assert result.exit_code == 0
    res = 'created versioned archive <DataArchive local://my_first_archive>'
    assert result.output.strip() == res

    result = runner.invoke(cli, prefix + ['filter'])
    assert result.exit_code == 0
    assert 'my_first_archive' in result.output.strip().split('\n')

    assert len(result.output.strip().split('\n')) == 1
    # test the actual creation of the object from the api side
    assert len(list(api2.filter())) == 1
    archive = api2.get_archive('my_first_archive')
    assert archive.archive_name == 'my_first_archive'

    # testing the `metadata` option
    result = runner.invoke(cli, prefix + ['metadata', 'my_first_archive'])
    assert result.exit_code == 0
    metadata = ast.literal_eval(result.output)
    assert metadata['description'] == 'My test data archive'

    # test the api side of the operation
    assert u'My test data archive' == archive.get_metadata()['description']

    with runner.isolated_filesystem():
        with open('hello.txt', 'w') as f:
            f.write('Hoo Yah! Stay Stoked!')

        # update using CLI
        result = runner.invoke(
            cli,
            prefix + [
                'update',
                'my_first_archive',
                'hello.txt',
                '--source',
                'Surfers Journal'])

        assert result.exit_code == 0

        # assert that we get update feedback
        expected = 'uploaded data to <DataArchive local://my_first_archive>'
        assert expected in result.output

        # lets read the file to make sure it remains unchanged
        with open('hello.txt', 'r') as f:
            data = f.read()
            assert data == 'Hoo Yah! Stay Stoked!'

        # Try re-upload
        result = runner.invoke(
            cli,
            prefix + [
                'update',
                'my_first_archive',
                'hello.txt',
                '--source',
                'Surfers Journal'])

        assert result.exit_code == 0
        # assert that we get update feedback
        intended_output = ('uploaded data to <DataArchive '
                           'local://my_first_archive>. version remains 0.0.1.')

        assert intended_output == result.output.strip()

    # this is testing the feed through on the api
    with api2.get_archive(list(api2.filter())[0]).open('r') as f:
        data = f.read()
        assert data == 'Hoo Yah! Stay Stoked!'

    # lets check to make sure our metadata update also passed through
    assert 'Surfers Journal' == api2.get_archive(
        list(api2.filter())[0]).get_metadata()['source']

    # test to assert metadata update
    # test to assert file content change

    with runner.isolated_filesystem():

        result = runner.invoke(cli,
                               prefix + ['update',
                                         'my_first_archive',
                                         '--bumpversion',
                                         'minor',
                                         '--string',
                                         'new version data'])
        assert result.exit_code == 0

        result = runner.invoke(cli, prefix + ['cat', 'my_first_archive'])
        assert result.exit_code == 0

        'new version data' in result.output

        result = runner.invoke(cli,
                               prefix + ['download',
                                         'my_first_archive',
                                         'here.txt',
                                         '--version',
                                         '0.0.1'])
        assert result.exit_code == 0

        'Hoo Yah! Stay Stoked!' in result.output

        # test download of previous version
        result = runner.invoke(cli,
                               prefix + ['download',
                                         'my_first_archive',
                                         'here.txt',
                                         '--version',
                                         '0.0.1'])
        assert result.exit_code == 0

        with open('here.txt', 'r') as downloaded:
            assert downloaded.read() == 'Hoo Yah! Stay Stoked!'

        # test download of nonexistant version (should fail without overwriting
        # file)
        result = runner.invoke(cli,
                               prefix + ['download',
                                         'my_first_archive',
                                         'here.txt',
                                         '--version',
                                         '3.0'])
        assert result.exit_code != 0

        with open('here.txt', 'r') as downloaded:
            assert downloaded.read() == 'Hoo Yah! Stay Stoked!'

        os.remove('here.txt')

    # teardown
    result = runner.invoke(cli, prefix + ['delete', 'my_first_archive'])

    result = runner.invoke(cli, prefix + ['filter'])
    assert result.exit_code == 0
    assert result.output.strip() == ''

    assert len(list(api2.filter())) == 0


def test_cli_unversioned(test_config):

    profile, temp_file = test_config

    prefix = ['--config-file', temp_file, '--profile', 'myapi']

    api2 = get_api(profile=profile, config_file=temp_file)

    runner = CliRunner()

    # test for configure and create archive
    result = runner.invoke(
        cli,
        prefix + [
            'create', 'unversioned', '--not-versioned'])

    assert result.exit_code == 0
    res = 'created archive <DataArchive local://unversioned>'
    assert result.output.strip() == res

    result = runner.invoke(cli, prefix + ['filter'])
    assert result.exit_code == 0
    assert ['unversioned'] == [result.output.strip()]

    # test the actual creation of the object from the api side
    assert len(list(api2.filter())) == 1
    archive = api2.get_archive('unversioned')
    assert archive.archive_name == 'unversioned'

    with runner.isolated_filesystem():
        with open('hello.txt', 'w') as f:
            f.write('un-versioned data')

        # update using CLI
        result = runner.invoke(
            cli,
            prefix + [
                'update',
                'unversioned',
                'hello.txt',
                '--dependency',
                'arch1',
                '--dependency',
                'arch2'])

        assert result.exit_code == 0

        # assert that we get update feedback
        expected = 'uploaded data to <DataArchive local://unversioned>.'
        assert expected == result.output.strip()

        # Try re-upload
        result = runner.invoke(
            cli,
            prefix + [
                'update',
                'unversioned',
                '--string',
                'new content'])

        assert result.exit_code == 0

        # assert that we get update feedback
        intended_output = 'uploaded data to <DataArchive local://unversioned>.'

        assert intended_output == result.output.strip()

    with runner.isolated_filesystem():

        # test download
        result = runner.invoke(cli, prefix +
                               ['download', 'unversioned', 'here.txt'])
        assert result.exit_code == 0

        with open('here.txt', 'r') as downloaded:
            assert downloaded.read() == 'new content'

        # test download with 'latest' version argument'
        result = runner.invoke(
            cli, prefix + [
                'download', 'unversioned', 'here.txt', '--version', 'latest'])

        assert result.exit_code != 0

        # test download with incorrect version argument
        result = runner.invoke(
            cli, prefix + [
                'download', 'unversioned', 'here.txt', '--version', '0.0.1'])

        assert result.exit_code != 0

        os.remove('here.txt')

    # teardown
    result = runner.invoke(cli, prefix + ['delete', 'unversioned'])

    result = runner.invoke(cli, prefix + ['filter'])
    assert result.exit_code == 0
    assert result.output.strip() == ''

    assert len(list(api2.filter())) == 0


def test_specified_requirements(preloaded_config):
    '''
    Test download commands with a mix of requirements file, explicit, and
    unspecified version requirements
    '''

    profile, temp_file = preloaded_config

    # Create a requirements file and

    runner = CliRunner()

    prefix = [
        '--config-file', '{}'.format(temp_file),
        '--profile', 'myapi',
        '--requirements', 'requirements_data_test1.txt']

    with runner.isolated_filesystem():

        # Create requirements file

        with open('requirements_data_test1.txt', 'w+') as reqs:
            reqs.write('req_1==1.0\n')
            reqs.write('req_2==0.0.1a2\n')

        # Download req_1 with version from requirements file

        result = runner.invoke(
            cli,
            prefix + ['download', 'req_1', 'local_req_1.txt'])

        assert result.exit_code == 0

        with open('local_req_1.txt', 'r') as f:
            assert f.read() == 'this is archive req_1 version 1.0'

        # Download req_2 with version from requirements file

        result = runner.invoke(
            cli,
            prefix + ['download', 'req_2', 'local_req_2.txt'])

        assert result.exit_code == 0

        with open('local_req_2.txt', 'r') as f:
            assert f.read() == 'this is archive req_2 version 0.0.1a2'

        # Download req_3 with version latest version (req_3 not in requirements
        # file)

        result = runner.invoke(
            cli,
            prefix + ['download', 'req_3', 'local_req_3.txt'])

        assert result.exit_code == 0

        with open('local_req_3.txt', 'r') as f:
            assert f.read() == 'this is archive req_3 version 1.1'


def test_versions(preloaded_config):
    '''
    Test "versions" CLI command with preloaded archive/config file
    '''

    profile, temp_file = preloaded_config

    # Create a requirements file and

    runner = CliRunner()

    prefix = [
        '--config-file', '{}'.format(temp_file),
        '--profile', 'myapi',
        '--requirements', 'requirements_data_test1.txt']

    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            prefix + ['versions', 'req_3'])

        assert result.exit_code == 0
        versions = ast.literal_eval(result.output)

        assert ['1.0', '1.1a1', '1.1'] == versions


def test_history(preloaded_config):
    '''
    Test "history" CLI command with preloaded archive/config file
    '''

    profile, temp_file = preloaded_config

    # Create a requirements file and

    runner = CliRunner()

    prefix = [
        '--config-file', '{}'.format(temp_file),
        '--profile', 'myapi',
        '--requirements', 'requirements_data_test1.txt']

    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            prefix + ['history', 'req_3'])

        assert result.exit_code == 0
        history = ast.literal_eval(result.output)
        assert len(history) == 3


def test_alternate_versions(preloaded_config):
    '''
    Assert requirements file can be superceeded by explicit version
    specification
    '''

    profile, temp_file = preloaded_config

    # Create a requirements file and

    runner = CliRunner()

    prefix = [
        '--config-file', '{}'.format(temp_file),
        '--profile', 'myapi',
        '--requirements', 'requirements_data_test2.txt']

    with runner.isolated_filesystem():

        # Create requirements file

        with open('requirements_data_test1.txt', 'w+') as reqs:
            reqs.write('req_1==1.0\n')
            reqs.write('req_2==0.0.1a2\n')

        # Download req_1 with version from requirements file

        result = runner.invoke(
            cli, prefix + [
                'download', 'req_1', 'local_req_1.txt', '--version', '0.1'])

        assert result.exit_code == 0

        with open('local_req_1.txt', 'r') as f:
            assert f.read() == 'this is archive req_1 version 0.1'

        # Download req_2 with version from requirements file

        result = runner.invoke(
            cli, prefix + [
                'download', 'req_2', 'local_req_2.txt', '--version', '0.0.1'])

        assert result.exit_code == 0

        with open('local_req_2.txt', 'r') as f:
            assert f.read() == 'this is archive req_2 version 0.0.1'

        # Download req_3 with version from requirements file

        result = runner.invoke(
            cli, prefix + [
                'download', 'req_3', 'local_req_3.txt', '--version', '1.1a1'])

        assert result.exit_code == 0

        with open('local_req_3.txt', 'r') as f:
            assert f.read() == 'this is archive req_3 version 1.1a1'


def test_kwarg_handling(preloaded_config):
    '''
    Assert errors raised when attempting to pull invalid versions
    '''

    profile, temp_file = preloaded_config

    # Create a requirements file and

    runner = CliRunner()

    prefix = [
        '--config-file', '{}'.format(temp_file),
        '--profile', 'myapi']

    # Assert error raised on improper arg

    result = runner.invoke(
        cli,
        prefix + [
            'update_metadata', 'req_1', 'something', '--description', 'other'])

    assert result.exception

    # Assert error raised on mid-kwarg arg

    result = runner.invoke(
        cli,
        prefix + [
            'update_metadata', 'req_1', '--description', 'something', 'other'])

    assert result.exception

    # Assert error raised on flag

    result = runner.invoke(
        cli,
        prefix + ['update_metadata', 'req_1', '--flag'])

    assert result.exception


def test_multiple_search(preloaded_config):
    '''
    Assert errors raised when attempting to pull invalid versions
    '''

    profile, temp_file = preloaded_config

    # Create a requirements file and

    runner = CliRunner()

    prefix = [
            '--config-file', '{}'.format(temp_file),
            '--profile', 'myapi']

    # Assert error raised on improper arg

    result = runner.invoke(
        cli,
        prefix + ['search'])

    assert len(result.output.strip().split('\n')) == 3

    # Assert error raised on mid-kwarg arg

    result = runner.invoke(
        cli,
        prefix + ['filter'])

    assert len(result.output.strip().split('\n')) == 3

    # Assert error raised on flag

    result = runner.invoke(
        cli,
        prefix + ['filter', '--pattern', 'req_[12]', '--engine', 'regex'])

    assert len(result.output.strip().split('\n')) == 2


def test_incorrect_versions(preloaded_config):
    '''
    Assert errors raised when attempting to pull invalid versions
    '''

    profile, temp_file = preloaded_config

    # Create a requirements file and

    runner = CliRunner()

    prefix = [
        '--config-file', '{}'.format(temp_file),
        '--profile', 'myapi',
        '--requirements', 'requirements_data_test3.txt']
    with runner.isolated_filesystem():

        # Create requirements file

        with open('requirements_data_test3.txt', 'w+') as reqs:
            reqs.write('req_1==5.0\n')
            reqs.write('req_2==0.3.1a2\n')

        # Download req_1 with version from requirements file

        result = runner.invoke(cli, prefix +
                               ['download', 'req_1', 'local_req_1.txt'])

        assert result.exception

        # Download req_2 with version from requirements file

        result = runner.invoke(
            cli, prefix + [
                'download', 'req_2', 'local_req_2.txt', '--version', 'latest'])

        assert result.exit_code == 0

        with open('local_req_2.txt', 'r') as f:
            assert f.read() == 'this is archive req_2 version 0.0.1'

        # Download req_3 with version from requirements file

        result = runner.invoke(
            cli, prefix + [
                'download', 'req_3', 'local_req_3.txt', '--version', '4.2'])

        assert result.exception


def test_dependency_parsing(test_config):
    '''
    Update archive dependencies across versions from the CLI
    '''

    profile, temp_file = test_config

    api = get_api(profile=profile, config_file=temp_file)

    runner = CliRunner()

    prefix = [
        '--config-file', '{}'.format(temp_file),
        '--profile',
        'myapi']

    arch1 = api.create('dep_archive')

    with runner.isolated_filesystem():

        with open('my_new_test_file.txt', 'w+') as to_update:
            to_update.write(u'test test test')

        result = runner.invoke(cli,
                               prefix + ['update',
                                         'dep_archive',
                                         'my_new_test_file.txt',
                                         '--bumpversion',
                                         'minor',
                                         '--dependency',
                                         'arch1==0.1.0',
                                         '--dependency',
                                         'arch2'])
        assert result.exit_code == 0

        assert arch1.get_latest_version() == '0.1.0'
        with arch1.open('r') as f:
            assert f.read() == u'test test test'

        assert arch1.get_dependencies(version='0.1.0') == {
            'arch1': '0.1.0', 'arch2': None}

        result = runner.invoke(cli,
                               prefix + ['set_dependencies',
                                         'dep_archive',
                                         '--dependency',
                                         'arch1==0.2.0',
                                         '--dependency',
                                         'arch2==0.0.1'])

        assert result.exit_code == 0
        assert arch1.get_dependencies(
            version='0.1.0') == {
            'arch1': '0.2.0',
            'arch2': '0.0.1'}

        with open('my_new_test_file.txt', 'w+') as to_update:
            to_update.write(u'test test test two three four')

        result = runner.invoke(cli,
                               prefix + ['update',
                                         'dep_archive',
                                         'my_new_test_file.txt',
                                         '--bumpversion',
                                         'minor',
                                         '--dependency',
                                         'arch1==0.2.0',
                                         '--dependency',
                                         'arch2==0.0.1'])

        assert result.exit_code == 0

        assert arch1.get_dependencies(
            version='0.1.0') == {
            'arch1': '0.2.0',
            'arch2': '0.0.1'}

        result = runner.invoke(cli, prefix +
                               ['get_dependencies', 'dep_archive'])

        assert result.exit_code == 0

        assert 'arch1==0.2.0' in result.output
        assert 'arch2==0.0.1' in result.output

        result = runner.invoke(
            cli, prefix + [
                'get_dependencies', 'dep_archive', '--version', '0.1'])

        assert result.exit_code == 0

        assert 'arch1==0.2.0' in result.output
        assert 'arch2==0.0.1' in result.output

        result = runner.invoke(cli,
                               prefix + ['set_dependencies',
                                         'dep_archive',
                                         '--dependency',
                                         'arch1==0.2.0',
                                         '--dependency',
                                         'arch2'])

        assert result.exit_code == 0

        result = runner.invoke(
            cli, prefix + [
                'get_dependencies', 'dep_archive'])

        assert result.exit_code == 0

        assert 'arch1==0.2.0' in result.output
        assert 'arch2' in result.output
        assert 'arch2==' not in result.output

        os.remove('my_new_test_file.txt')

    api.delete_archive('dep_archive')


def test_update_metadata(test_config, monkeypatch):
    '''
    Update archive metadata with a description from the CLI
    '''

    profile, temp_file = test_config

    api = get_api(profile=profile, config_file=temp_file)

    runner = CliRunner()

    prefix = [
        '--config-file', '{}'.format(temp_file),
        '--profile', 'myapi']

    arch1 = api.create('my_next_archive')

    with runner.isolated_filesystem():

        with open('my_new_test_file.txt', 'w+') as to_update:
            to_update.write(u'test test test')

        def get_input_file(*args, **kwargs):
            return 'my_new_test_file.txt'

        # override click.prompt
        monkeypatch.setattr('click.prompt', get_input_file)

        result = runner.invoke(
            cli, prefix + [
                'update', 'my_next_archive'])

        assert result.exit_code == 0

        result = runner.invoke(cli,
                               prefix + ['update_metadata',
                                         'my_next_archive',
                                         '--description',
                                         'some_description'])
        assert result.exit_code == 0
        assert arch1.get_metadata() == {'description': 'some_description'}

        os.remove('my_new_test_file.txt')

        result = runner.invoke(
            cli,
            prefix + ['update', 'my_next_archive', '--string'],
            input='my new contents\ncan be piped in')

        assert result.exit_code == 0

        result = runner.invoke(cli, prefix + ['cat', 'my_next_archive'])

        assert result.exit_code == 0

        assert 'my new contents' in result.output.strip().split('\n')
        assert 'can be piped in' in result.output.strip().split('\n')

    arch1.delete()


def test_sufficient_configuration(manager_with_spec, tempdir):
    '''
    Test writing an api with required user config to a config file and then
    running configure.
    '''

    # Create an appropriately specified API
    api = DataAPI(
        username='My Name',
        contact='my.email@example.com')

    # Attach a manager which requires username, contact
    api.attach_manager(manager_with_spec)

    # Export the API to a file
    config_file = os.path.join(tempdir, '.datafs.yml')
    to_config_file(api=api, config_file=config_file, profile='conftest')

    runner = CliRunner()

    prefix = ['--config-file', config_file, '--profile', 'conftest']

    # Test the configuration
    result = runner.invoke(cli, prefix + ['configure'])
    assert result.exit_code == 0


def test_insufficient_configuration(manager_with_spec, tempdir):
    '''
    Test writing an api with required user config to a config file and then
    running configure without sufficient user_config.
    '''

    # Create an insufficiently specified API
    api = DataAPI(username='My Name')

    # Attach a manager which requires username, contact
    api.attach_manager(manager_with_spec)

    # Export the API to a file
    config_file = os.path.join(tempdir, '.datafs.yml')
    to_config_file(api=api, config_file=config_file, profile='conftest')

    runner = CliRunner()

    prefix = ['--config-file', config_file, '--profile', 'conftest']

    # Test the configuration and make sure an exception is raised
    result = runner.invoke(cli, prefix + ['configure'])
    assert result.exception


def test_manual_configuration(manager_with_spec, tempdir):
    '''
    Test writing an api with required user config to a config file and then
    running configure user_config specified as keyword arguments
    '''

    # Create an insufficiently specified API
    api = DataAPI(username='My Name')

    # Attach a manager which requires username, contact
    api.attach_manager(manager_with_spec)

    # Export the API to a file
    config_file = os.path.join(tempdir, '.datafs.yml')
    to_config_file(api=api, config_file=config_file, profile='conftest')

    runner = CliRunner()

    prefix = ['--config-file', config_file, '--profile', 'conftest']

    # Test the configuration and make sure an exception is raised
    result = runner.invoke(cli, prefix + [
        'configure',
        '--contact',
        '"my_email@domain.com'])

    assert result.exit_code == 0


def test_helper_configuration(manager_with_spec, tempdir, monkeypatch):
    '''
    Test writing an api with required user config to a config file and then
    running configure user_config with the flag --helper
    '''

    # Create an insufficiently specified API
    api = DataAPI(username='My Name')

    # Attach a manager which requires username, contact
    api.attach_manager(manager_with_spec)

    # Export the API to a file
    config_file = os.path.join(tempdir, '.datafs.yml')
    to_config_file(api=api, config_file=config_file, profile='conftest')

    assert 'contact' not in api.user_config

    runner = CliRunner()

    prefix = ['--config-file', config_file, '--profile', 'conftest']

    def get_user_email(*args, **kwargs):
        return "my_email@domain.com"

    # override click.prompt
    monkeypatch.setattr('click.prompt', get_user_email)

    # Test the helper with the appropriate input stream
    result = runner.invoke(
        cli,
        prefix + ['configure', '--helper']
    )

    assert result.exit_code == 0

    api2 = get_api(config_file=config_file, profile='conftest')
    assert api2.user_config['contact'] == "my_email@domain.com"
