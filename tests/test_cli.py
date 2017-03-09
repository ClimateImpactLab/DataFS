from datafs.managers.manager_dynamo import DynamoDBManager
from datafs.datafs import cli
from datafs import DataAPI, get_api, to_config_file
import os
from click.testing import CliRunner
import pytest
import ast
import re


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
def sample_config(manager_table, temp_dir_mod, temp_file):
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
def preloaded_config(sample_config):
    '''
    Prepare a manager/auth config with 3 archives, each having 3 versions

    .. note::

        To save on test runtime, scope == module. Tests should not modify
        these archives.

    '''

    profile, temp_file = sample_config

    api = get_api(profile=profile, config_file=temp_file)

    # Set up a couple archives with multiple versions

    arch1 = api.create('/req/arch1')
    arch2 = api.create('/req/arch2')
    arch3 = api.create('/req/arch3')

    with arch1.open('w+', bumpversion='minor', message='bumping to 0.1') as f:
        f.write(u'this is archive /req/arch1 version 0.1')

    with arch1.open('w+', bumpversion='major', message='bumping to 1.0') as f:
        f.write(u'this is archive /req/arch1 version 1.0')

    with arch1.open('w+', bumpversion='minor', message='bumping to 1.1') as f:
        f.write(u'this is archive /req/arch1 version 1.1')

    arch1_versions = arch1.get_versions()
    assert '0.1' in arch1_versions
    assert '1.0' in arch1_versions
    assert '1.1' in arch1_versions

    with arch2.open('w+', prerelease='alpha') as f:
        f.write(u'this is archive /req/arch2 version 0.0.1a1')

    with arch2.open('w+', prerelease='alpha') as f:
        f.write(u'this is archive /req/arch2 version 0.0.1a2')

    with arch2.open('w+', bumpversion='patch') as f:
        f.write(u'this is archive /req/arch2 version 0.0.1')

    arch2_versions = arch2.get_versions()
    assert '0.0.1a1' in arch2_versions
    assert '0.0.1a2' in arch2_versions
    assert '0.0.1' in arch2_versions

    with arch3.open('w+', bumpversion='major') as f:
        f.write(u'this is archive /req/arch3 version 1.0')

    with arch3.open('w+', bumpversion='minor', prerelease='alpha') as f:
        f.write(u'this is archive /req/arch3 version 1.1a1')

    with arch3.open('w+', bumpversion='minor') as f:
        f.write(u'this is archive /req/arch3 version 1.1')

    arch3_versions = arch3.get_versions()
    assert '1.0' in arch3_versions
    assert '1.1a1' in arch3_versions
    assert '1.1' in arch3_versions

    # Set up an unversioned archive with multiple versions

    arch_uver = api.create('uver1', versioned=False)

    with arch_uver.open('w+', message='bumping to 0.1') as f:
        f.write(u'this is archive uver1 version 0.1')

    with arch_uver.open('w+', message='bumping to 1.0') as f:
        f.write(u'this is archive uver1 version 1.0')

    with arch_uver.open('w+', message='bumping to 1.1') as f:
        f.write(u'this is archive uver1 version 1.1')

    arch_uver_versions = arch_uver.get_history()
    assert len(arch_uver_versions) == 3

    try:

        yield profile, temp_file

    finally:

        arch1.delete()
        arch2.delete()
        arch3.delete()
        arch_uver.delete()


@pytest.mark.cli
def test_cli_local(sample_config):

    profile, temp_file = sample_config

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

    assert len(result.output.strip().split('\n')) == len(list(api2.filter()))

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


@pytest.mark.cli
def test_cli_unversioned(sample_config):

    profile, temp_file = sample_config

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


@pytest.mark.cli
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
            reqs.write('/req/arch1==1.0\n')
            reqs.write('/req/arch2==0.0.1a2\n')

        # Download /req/arch1 with version from requirements file

        result = runner.invoke(
            cli,
            prefix + ['download', '/req/arch1', 'local_req_1.txt'])

        assert result.exit_code == 0

        with open('local_req_1.txt', 'r') as f:
            assert f.read() == 'this is archive /req/arch1 version 1.0'

        # Download /req/arch2 with version from requirements file

        result = runner.invoke(
            cli,
            prefix + ['download', '/req/arch2', 'local_req_2.txt'])

        assert result.exit_code == 0

        with open('local_req_2.txt', 'r') as f:
            assert f.read() == 'this is archive /req/arch2 version 0.0.1a2'

        # Download /req/arch3 with version latest version (/req/arch3 not in
        # requirements file)

        result = runner.invoke(
            cli,
            prefix + ['download', '/req/arch3', 'local_req_3.txt'])

        assert result.exit_code == 0

        with open('local_req_3.txt', 'r') as f:
            assert f.read() == 'this is archive /req/arch3 version 1.1'


@pytest.mark.cli
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
            prefix + ['versions', '/req/arch3'])

        assert result.exit_code == 0
        versions = ast.literal_eval(result.output)

        assert ['1.0', '1.1a1', '1.1'] == versions


@pytest.mark.cli
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
            prefix + ['history', '/req/arch3'])

        assert result.exit_code == 0
        history = ast.literal_eval(result.output)
        assert len(history) == 3


@pytest.mark.cli
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
            reqs.write('/req/arch1==1.0\n')
            reqs.write('/req/arch2==0.0.1a2\n')

        # Download /req/arch1 with version from requirements file

        result = runner.invoke(
            cli, prefix + [
                'download',
                '/req/arch1',
                'local_req_1.txt',
                '--version',
                '0.1'])

        assert result.exit_code == 0

        with open('local_req_1.txt', 'r') as f:
            assert f.read() == 'this is archive /req/arch1 version 0.1'

        # Download /req/arch2 with version from requirements file

        result = runner.invoke(
            cli, prefix + [
                'download',
                '/req/arch2',
                'local_req_2.txt',
                '--version',
                '0.0.1'])

        assert result.exit_code == 0

        with open('local_req_2.txt', 'r') as f:
            assert f.read() == 'this is archive /req/arch2 version 0.0.1'

        # Download /req/arch3 with version from requirements file

        result = runner.invoke(
            cli, prefix + [
                'download',
                '/req/arch3',
                'local_req_3.txt',
                '--version',
                '1.1a1'])

        assert result.exit_code == 0

        with open('local_req_3.txt', 'r') as f:
            assert f.read() == 'this is archive /req/arch3 version 1.1a1'


@pytest.mark.cli
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
            'update_metadata',
            '/req/arch1',
            'something',
            '--description',
            'other'])

    assert result.exception

    # Assert error raised on mid-kwarg arg

    result = runner.invoke(
        cli,
        prefix + [
            'update_metadata',
            '/req/arch1',
            '--description',
            'something',
            'other'])

    assert result.exception

    # Assert error raised on flag

    result = runner.invoke(
        cli,
        prefix + ['update_metadata', '/req/arch1', '--flag'])

    assert result.exception


@pytest.mark.cli
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

    assert len(result.output.strip().split('\n')) == 4

    # Assert error raised on mid-kwarg arg

    result = runner.invoke(
        cli,
        prefix + ['filter'])

    assert len(result.output.strip().split('\n')) == 4

    # Assert error raised on flag

    result = runner.invoke(
        cli,
        prefix + ['filter', '--pattern', '/req/arch[12]', '--engine', 'regex'])

    assert len(result.output.strip().split('\n')) == 2


@pytest.mark.cli
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
            reqs.write('/req/arch1==5.0\n')
            reqs.write('/req/arch2==0.3.1a2\n')

        # Download /req/arch1 with version from requirements file

        result = runner.invoke(cli, prefix +
                               ['download', '/req/arch1', 'local_req_1.txt'])

        assert result.exception

        # Download /req/arch2 with version from requirements file

        result = runner.invoke(
            cli, prefix + [
                'download',
                '/req/arch2',
                'local_req_2.txt',
                '--version',
                'latest'])

        assert result.exit_code == 0

        with open('local_req_2.txt', 'r') as f:
            assert f.read() == 'this is archive /req/arch2 version 0.0.1'

        # Download /req/arch3 with version from requirements file

        result = runner.invoke(
            cli, prefix + [
                'download',
                '/req/arch3',
                'local_req_3.txt',
                '--version',
                '4.2'])

        assert result.exception


@pytest.mark.cli
def test_dependency_parsing(sample_config):
    '''
    Update archive dependencies across versions from the CLI
    '''

    profile, temp_file = sample_config

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


@pytest.mark.cli
def test_update_metadata(sample_config, monkeypatch):
    '''
    Update archive metadata with a description from the CLI
    '''

    profile, temp_file = sample_config

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


@pytest.mark.cli
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


@pytest.mark.cli
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


@pytest.mark.cli
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


@pytest.mark.cli
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


@pytest.mark.cli
def test_listdir(preloaded_config):

    profile, temp_file = preloaded_config

    # Create a requirements file and

    runner = CliRunner()

    prefix = [
        '--config-file', '{}'.format(temp_file),
        '--profile', 'myapi',
        '--requirements', 'requirements_data_test3.txt']

    with runner.isolated_filesystem():

        result = runner.invoke(cli, prefix + ['listdir', 'local://req/'])

        assert result.exit_code == 0

        contents = map(lambda s: s.strip(), result.output.strip().split('\n'))

        assert len(contents) == 3

        for req in ['arch1', 'arch2', 'arch3']:
            assert req in contents


@pytest.mark.logging
@pytest.mark.cli
def test_versioned_logging(preloaded_config):
    '''
    Test logging cli features
    '''

    profile, temp_file = preloaded_config

    # Create a requirements file and

    runner = CliRunner()

    prefix = [
        '--config-file', '{}'.format(temp_file),
        '--profile', 'myapi']

    with runner.isolated_filesystem():

        # Download req_1 with version from requirements file

        result = runner.invoke(
            cli,
            prefix + ['log', '/req/arch1'])

    assert result.exit_code == 0

    log = result.output.strip()

    verstr_matcher = r'(version [0-9]+(\.[0-9]+){1,2} \(md5 \w+\))'

    versions = re.finditer(
        (r'(?P<ver>' +
            verstr_matcher +
            r'\n([^\n]*(\n(?!' +
            verstr_matcher + r'))?)+)'),
        log)

    api = get_api(config_file=temp_file, profile='myapi')

    arch = api.get_archive('/req/arch1')

    hist = arch.get_history()

    for i, vermatch in enumerate(reversed(list(versions))):
        verstr = vermatch.group('ver')
        verhist = hist[i]

        assert verhist['checksum'] in verstr
        assert verhist['message'] in verstr

        for attr, val in verhist['user_config'].items():
            assert attr in verstr
            assert val in verstr


@pytest.mark.logging
@pytest.mark.cli
def test_unversioned_logging(preloaded_config):
    '''
    Test logging cli features
    '''

    profile, temp_file = preloaded_config

    # Create a requirements file and

    runner = CliRunner()

    prefix = [
        '--config-file', '{}'.format(temp_file),
        '--profile', 'myapi',
        '--requirements', 'requirements_data_test3.txt']

    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            prefix + ['listdir', '/req/', '--authority_name', 'local'])

        assert result.exit_code == 0

        contents = map(lambda s: s.strip(), result.output.strip().split('\n'))

        assert len(contents) == 3

        for req in ['arch1', 'arch2', 'arch3']:
            assert req in contents


@pytest.mark.cli
def test_listdir_noauth(preloaded_config):

    profile, temp_file = preloaded_config

    # Create a requirements file and

    runner = CliRunner()

    prefix = [
        '--config-file', '{}'.format(temp_file),
        '--profile', 'myapi',
        '--requirements', 'requirements_data_test3.txt']

    with runner.isolated_filesystem():

        result = runner.invoke(cli, prefix + ['listdir', '/req/'])

        assert result.exit_code == 0

        contents = map(lambda s: s.strip(), result.output.strip().split('\n'))

        assert len(contents) == 3

        for req in ['arch1', 'arch2', 'arch3']:
            assert req in contents


@pytest.mark.cli
def test_listdir_auth(preloaded_config):

    profile, temp_file = preloaded_config

    # Create a requirements file and

    runner = CliRunner()

    prefix = [
        '--config-file', '{}'.format(temp_file),
        '--profile', 'myapi']

    with runner.isolated_filesystem():

        # Download uver1 with version from requirements file

        result = runner.invoke(
            cli,
            prefix + ['log', 'uver1'])

    assert result.exit_code == 0

    log = result.output.strip()

    verstr_matcher = r'(update [0-9]+ \(md5 \w+\))'

    versions = re.finditer(
        (r'(?P<ver>' +
            verstr_matcher +
            r'\n([^\n]*(\n(?!' +
            verstr_matcher + r'))?)+)'),
        log)

    api = get_api(config_file=temp_file, profile='myapi')

    arch = api.get_archive('uver1')

    hist = arch.get_history()

    for i, vermatch in enumerate(reversed(list(versions))):
        verstr = vermatch.group('ver')
        verhist = hist[i]

        assert verhist['checksum'] in verstr
        assert verhist['message'] in verstr

        for attr, val in verhist['user_config'].items():
            assert attr in verstr
            assert val in verstr
