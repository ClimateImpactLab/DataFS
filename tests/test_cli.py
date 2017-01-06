from datafs.managers.manager_mongo import MongoDBManager
from datafs.managers.manager_dynamo import DynamoDBManager
from datafs.datafs import cli
from datafs import DataAPI, get_api, to_config_file
import tempfile
import os
import click
from click.testing import CliRunner
import pytest, shutil

try:
    from StringIO import StringIO

except ImportError:
    from io import StringIO




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


@pytest.yield_fixture(scope='module')
def manager_table():

    # setup manager table

    table_name = 'my-cli-test-table'

    manager = DynamoDBManager(table_name, 
                            session_args={ 
                                            'aws_access_key_id': "access-key-id-of-your-choice",
                                            'aws_secret_access_key': "secret-key-of-your-choice"}, 
                            resource_args={ 
                                            'endpoint_url':'http://localhost:8000/','region_name':'us-east-1'}
                            )

    manager.create_archive_table(table_name, raise_on_err=False)

    try:
        yield table_name

    finally:
        manager.delete_table(table_name)


@pytest.yield_fixture(scope='module')
def temp_dir():

    # setup data directory

    temp = tempfile.mkdtemp()

    try:
        yield temp.replace(os.sep, '/')
    
    finally:
        _close(temp)


@pytest.yield_fixture(scope='module')
def temp_file():
    tmp = tempfile.NamedTemporaryFile(delete=False)

    try:
        yield tmp.name.replace(os.sep, '/')

    finally:
        tmp.close()
        _close(tmp.name)


@pytest.yield_fixture(scope='module')
def test_config(manager_table, temp_dir, temp_file):
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
    cache: {{}}
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
'''.format(table=manager_table, dir=temp_dir)
    
    with open(temp_file, 'w+') as f:
        f.write(my_test_yaml)

    yield 'myapi', temp_file


def test_cli_local(test_config):

    profile, temp_file = test_config

    api2 = get_api(profile=profile, config_file=temp_file)

    runner = CliRunner()


    #test for configure and create archive
    result = runner.invoke(cli, ['--config-file', '{}'.format(temp_file), '--profile', 'myapi', 'create_archive', 'my_first_archive', '--description', 'My test data archive'])
    assert result.exit_code == 0
    assert result.output.strip() == 'created versioned archive <DataArchive local://my_first_archive>'

    #test the actual creation of the object from the api side
    assert len(api2.archives) == 1
    assert api2.archives[0].archive_name == 'my_first_archive'

    #testing the `metadata` option
    result = runner.invoke(cli, ['--config-file', '{}'.format(temp_file), '--profile', 'myapi', 'metadata', 'my_first_archive'])
    assert result.exit_code == 0
    assert "'description': 'My test data archive'" in result.output or "u'description': u'My test data archive'" in result.output
    #test the api side of the operation
    assert u'My test data archive' in api2.archives[0].get_metadata().values()



    result = runner.invoke(cli, ['--config-file', '{}'.format(temp_file), '--profile', 'myapi', 'list'])
    #print result.output
    assert result.exit_code == 0
    assert 'my_first_archive' in result.output
    assert api2.archives[0].archive_name == 'my_first_archive'


    with runner.isolated_filesystem():
        with open('hello.txt', 'w') as f:
            f.write('Hoo Yah! Stay Stoked!')

        #use testing suite to make command line update
        result = runner.invoke(cli, ['--config-file', '{}'.format(temp_file), '--profile', 'myapi', 'upload', 'my_first_archive', 'hello.txt', '--source', 'Surfers Journal'])
        assert result.exit_code == 0
        #assert that we get upload feedback
        assert 'uploaded data to <DataArchive local://my_first_archive>' in result.output
        #lets read the file to make sure it says what we want
        with open('hello.txt','r') as f:
            data = f.read()
            assert data == 'Hoo Yah! Stay Stoked!'
        print result.output

    #this is testing the feed through on the api
    with api2.archives[0].open('r') as f:
        data = f.read()
        assert data == 'Hoo Yah! Stay Stoked!'

    #lets check to make sure our metadata update also passed through
    assert 'Surfers Journal' ==  api2.archives[0].get_metadata()['source']

    
    #test to assert metadata update
    #test to assert file content change

    
    with runner.isolated_filesystem():

        with open('here.txt', 'w+') as to_upload:
            to_upload.write('new version data')

        result = runner.invoke(cli, ['--config-file', '{}'.format(temp_file), '--profile', 'myapi', 'upload', 'my_first_archive', 'here.txt', '--bumpversion', 'minor'])
        assert result.exit_code == 0

        os.remove('here.txt')

        result = runner.invoke(cli, ['--config-file', '{}'.format(temp_file), '--profile', 'myapi', 'download', 'my_first_archive', 'here.txt'])
        assert result.exit_code == 0

        with open('here.txt', 'r') as downloaded:
            assert downloaded.read() == 'new version data'

        result = runner.invoke(cli, ['--config-file', '{}'.format(temp_file), '--profile', 'myapi', 'download', 'my_first_archive', 'here.txt', '--version', '0.0.1'])
        assert result.exit_code == 0

        with open('here.txt', 'r') as downloaded:
            assert downloaded.read() == 'Hoo Yah! Stay Stoked!'

        # test download of nonexistant version (should fail without overwriting file)
        result = runner.invoke(cli, ['--config-file', '{}'.format(temp_file), '--profile', 'myapi', 'download', 'my_first_archive', 'here.txt', '--version', '3.0'])
        assert result.exit_code != 0

        with open('here.txt', 'r') as downloaded:
            assert downloaded.read() == 'Hoo Yah! Stay Stoked!'

        os.remove('here.txt')




    #teardown
    api2.archives[0].delete()



@pytest.yield_fixture(scope='module')
def preloaded_config(test_config):

    profile, temp_file = test_config

    api = get_api(profile=profile, config_file=temp_file)

    
    # Set up a couple archives with multiple versions
    
    arch1 = api.create_archive('req_1')
    arch2 = api.create_archive('req_2')
    arch3 = api.create_archive('req_3')

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

    yield profile, temp_file

    arch1.delete()
    arch2.delete()
    arch3.delete()


def test_specified_requirements(preloaded_config):

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
            prefix + ['download', 'req_1','local_req_1.txt'])

        assert result.exit_code == 0

        with open('local_req_1.txt', 'r') as f:
            assert f.read() == 'this is archive req_1 version 1.0'
        

        # Download req_2 with version from requirements file

        result = runner.invoke(
            cli, 
            prefix + ['download', 'req_2','local_req_2.txt'])

        assert result.exit_code == 0

        with open('local_req_2.txt', 'r') as f:
            assert f.read() == 'this is archive req_2 version 0.0.1a2'
        

        # Download req_3 with version latest version (req_3 not in requirements file)
        
        result = runner.invoke(
            cli, 
            prefix + ['download', 'req_3','local_req_3.txt'])

        assert result.exit_code == 0

        with open('local_req_3.txt', 'r') as f:
            assert f.read() == 'this is archive req_3 version 1.1'



def test_alternate_versions(preloaded_config):

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
        
        result = runner.invoke(cli, prefix + 
            ['download', 'req_1','local_req_1.txt', '--version', '0.1'])

        assert result.exit_code == 0

        with open('local_req_1.txt', 'r') as f:
            assert f.read() == 'this is archive req_1 version 0.1'
        

        # Download req_2 with version from requirements file

        result = runner.invoke(cli, prefix + 
            ['download', 'req_2','local_req_2.txt', '--version', '0.0.1'])

        assert result.exit_code == 0

        with open('local_req_2.txt', 'r') as f:
            assert f.read() == 'this is archive req_2 version 0.0.1'
        

        # Download req_3 with version from requirements file
        
        result = runner.invoke(cli, prefix + 
            ['download', 'req_3','local_req_3.txt', '--version', '1.1a1'])

        assert result.exit_code == 0

        with open('local_req_3.txt', 'r') as f:
            assert f.read() == 'this is archive req_3 version 1.1a1'



def test_incorrect_versions(preloaded_config):

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
            ['download', 'req_1','local_req_1.txt'])

        assert result.exception


        # Download req_2 with version from requirements file

        result = runner.invoke(cli, prefix + 
            ['download', 'req_2','local_req_2.txt', '--version', 'latest'])

        assert result.exit_code == 0

        with open('local_req_2.txt', 'r') as f:
            assert f.read() == 'this is archive req_2 version 0.0.1'
        

        # Download req_3 with version from requirements file
        
        result = runner.invoke(cli, prefix + 
            ['download', 'req_3','local_req_3.txt', '--version', '4.2'])

        assert result.exception

def test_dependency_parsing(test_config):

    profile, temp_file = test_config

    api = get_api(profile=profile, config_file=temp_file)

    runner = CliRunner()

    prefix = [
                '--config-file', '{}'.format(temp_file), 
                '--profile', 
                'myapi']

    arch1 = api.create_archive('my_first_archive')

    with runner.isolated_filesystem():

        with open('my_new_test_file.txt', 'w+') as to_upload:
            to_upload.write(u'test test test')

        result = runner.invoke(cli, prefix + ['upload', 'my_first_archive', 'my_new_test_file.txt', '--bumpversion', 'minor' , '--dependency' , 'arch1==0.1.0', '--dependency', 'arch2'])
        assert result.exit_code == 0

        assert arch1.get_latest_version() == '0.1.0'
        with arch1.open('r') as f:
            assert f.read() == u'test test test'        

        assert arch1.get_dependencies(version='0.1.0') == {'arch1': '0.1.0', 'arch2': None}

        result = runner.invoke(cli, prefix + ['set_dependencies', 'my_first_archive','--dependency' , 'arch1==0.2.0', '--dependency', 'arch2==0.0.1'])

        assert result.exit_code == 0
        assert arch1.get_dependencies(version='0.1.0') == {'arch1': '0.2.0', 'arch2': '0.0.1'}
        

        with open('my_new_test_file.txt', 'w+') as to_upload:
            to_upload.write(u'test test test two three four')

        result = runner.invoke(cli, prefix + ['upload', 'my_first_archive', 'my_new_test_file.txt', '--bumpversion', 'minor' , '--dependency' , 'arch1==0.2.0', '--dependency', 'arch2==0.0.1'])

        assert result.exit_code == 0

        assert arch1.get_dependencies(version='0.1.0') == {'arch1': '0.2.0', 'arch2': '0.0.1'}

        

        os.remove('my_new_test_file.txt')


def test_update_metadata(test_config):

    profile, temp_file = test_config

    api = get_api(profile=profile, config_file=temp_file)

    runner = CliRunner()

    prefix = [
                '--config-file', '{}'.format(temp_file), 
                '--profile', 'myapi']

    arch1 = api.create_archive('my_next_archive')

    with runner.isolated_filesystem():

        with open('my_new_test_file.txt', 'w+') as to_upload:
            to_upload.write(u'test test test')

        result = runner.invoke(cli, prefix + ['upload', 'my_next_archive', 'my_new_test_file.txt'])
        assert result.exit_code == 0

        result = runner.invoke(cli, prefix + ['update_metadata', 'my_next_archive', '--description', 'some_description'])
        assert result.exit_code == 0
        assert arch1.get_metadata() == {'description': 'some_description'}

        
        os.remove('my_new_test_file.txt')


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
