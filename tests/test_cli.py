from datafs.managers.manager_mongo import MongoDBManager
from datafs.managers.manager_dynamo import DynamoDBManager
import tempfile
import os
from click.testing import CliRunner
from datafs import get_api
from datafs.datafs import cli
from contextlib import contextmanager
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


@pytest.yield_fixture(scope='function')
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


@pytest.yield_fixture(scope='function')
def temp_dir():

    # setup data directory

    temp = tempfile.mkdtemp()

    try:
        yield temp.replace(os.sep, '/')
    
    finally:
        _close(temp)


@pytest.yield_fixture(scope='function')
def temp_file():
    tmp = tempfile.NamedTemporaryFile(delete=False)

    try:
        yield tmp.name.replace(os.sep, '/')

    finally:
        tmp.close()
        _close(tmp.name)


def temp_update_file():
    tmp = tempfile.NamedTemporaryFile(delete=False).name.replace(os.sep, '/')

    with open(tmp, 'w+') as f:
        f.write('some text to display')

    return tmp


def test_cli_local(manager_table, temp_dir, temp_file):

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

    api2 = get_api(profile='myapi', config_file=temp_file)

    runner = CliRunner()


    #test for configure and create archive
    result = runner.invoke(cli, ['--config-file', '{}'.format(temp_file), '--profile', 'myapi', 'create_archive', 'my_first_archive', '--description', 'My test data archive'])
    assert result.exit_code == 0
    assert result.output.strip() == 'created archive <DataArchive local://my_first_archive>'

    #test the actual creation of the object from the api side
    assert len(api2.archives) == 1
    assert api2.archives[0].archive_name == 'my_first_archive'

    #testing the `metadata` option
    result = runner.invoke(cli, ['--config-file', '{}'.format(temp_file), '--profile', 'myapi', 'metadata', 'my_first_archive'])
    assert result.exit_code == 0
    assert "'description': 'My test data archive'" in result.output or "u'description': u'My test data archive'" in result.output
    #test the api side of the operation
    assert u'My test data archive' in api2.archives[0].metadata.values()



    result = runner.invoke(cli, ['--config-file', '{}'.format(temp_file), '--profile', 'myapi', 'list'])
    #print result.output
    assert 'my_first_archive' in result.output
    assert api2.archives[0].archive_name == 'my_first_archive'


    #test upload
    with runner.isolated_filesystem():
        with open('hello.txt', 'w') as f:
            f.write('Hoo Yah! Stay Stoked!')

    result = runner.invoke(cli, ['--config-file', '{}'.format(temp_file), '--profile', 'myapi', 'upload', 'my_first_archive', 'hello.txt', '--source', 'Surfers Journal'])
    assert 'uploaded data to <DataArchive local://my_first_archive>' in result.output
    assert result.output == 'Hoo Yah! Stay Stoked!'


    


    result = runner.invoke(cli, ['--config-file', '{}'.format(temp_file), '--profile', 'myapi', 'versions', 'my_first_archive'])
    #print result.output

    result = runner.invoke(cli, ['--config-file', '{}'.format(temp_file), '--profile', 'myapi', 'metadata', 'my_first_archive'])



if __name__ == '__main__':
    ctx_manager_table = contextmanager(manager_table)
    ctx_temp_dir = contextmanager(temp_dir)
    ctx_temp_file = contextmanager(temp_file)

    with ctx_manager_table() as m, ctx_temp_dir() as tempdir, ctx_temp_file() as tmp:
        test_cli_local(m, tempdir, tmp)

