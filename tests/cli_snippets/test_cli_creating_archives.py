
from click.testing import CliRunner
from datafs.datafs import cli
from datafs import get_api
from contextlib import contextmanager
import shlex
import re
import pytest


def get_command(string):
    parsed = re.search(
        r'\ *\$ (?P<cmd>datafs[^\n]+)(?P<response>(\n\ +[^\n]+)*)',
        string)

    command = shlex.split(parsed.group('cmd'))[1:]
    response = '\n'.join(map(
        lambda s: s.strip(),
        parsed.group('response').strip().split('\n')))

    lines = response.split('\n')
    if lines[0] == 'Traceback (most recent call last):':
        response = None
        exception = ' '.join(map(lambda s: s.strip(), lines[2:]))
    else:
        exception = None

    return command, response, exception


def validate_command(config, command, error=False):

    runner, api, config_file, prefix = config

    command, response, exception = get_command(command)

    result = runner.invoke(cli, prefix + command)

    if error:
        assert result.exit_code != 0
        fmt = result.exc_info[0].__name__ + ': ' + str(result.exc_info[1])
        assert exception == fmt
    else:
        assert result.exit_code == 0
        assert result.output.strip() == response


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


@pytest.mark.cli_snippets
@pytest.yield_fixture(scope='function')
def setup():
    config_file = 'examples/snippets/resources/datafs.yml'
    table_name = 'DataFiles'
    archive_name = 'my_archive_name'

    with setup_runner_resource(config_file, table_name, archive_name) as setup:
        yield setup


@pytest.mark.cli_snippets
@pytest.yield_fixture(scope='function')
def setup_dual_auth():
    config_file = 'examples/snippets/resources/datafs_dual_auth.yml'
    table_name = 'OtherFiles'
    archive_name = 'my_archive_name'

    with setup_runner_resource(config_file, table_name, archive_name) as setup:
        yield setup


@pytest.mark.cli_snippets
def test_cli_snippet_1(setup):

    runner, api, config_file, prefix = setup

    validate_command(setup, '''

.. EXAMPLE-BLOCK-1-START

.. code-block:: bash

    $ datafs create my_archive_name
    created versioned archive <DataArchive local://my_archive_name>

.. EXAMPLE-BLOCK-1-END

''')

    api.delete_archive('my_archive_name')


@pytest.mark.cli_snippets
def test_cli_snippet_2(setup_dual_auth):

    runner, api, config_file, prefix = setup_dual_auth

    validate_command(setup_dual_auth, '''

.. EXAMPLE-BLOCK-2-START

.. code-block:: bash

    $ datafs create my_archive_name --authority_name "my_authority"
    created versioned archive <DataArchive my_authority://my_archive_name>

.. EXAMPLE-BLOCK-2-END

''')

    api.delete_archive('my_archive_name')


@pytest.mark.cli_snippets
def test_cli_snippet_3(setup):

    runner, api, config_file, prefix = setup

    validate_command(setup, '''

.. EXAMPLE-BLOCK-3-START

.. code-block:: bash

    $ datafs create my_archive_name --description 'my test archive'
    created versioned archive <DataArchive local://my_archive_name>

.. EXAMPLE-BLOCK-3-END

''')

    api.delete_archive('my_archive_name')


@pytest.mark.cli_snippets
def test_cli_snippet_4(setup):

    runner, api, config_file, prefix = setup

    api.manager.set_required_archive_metadata({
        'description': 'Archive description'})

    validate_command(setup, '''

.. EXAMPLE-BLOCK-4-START

.. code-block:: bash

    $ datafs create my_archive_name --doi '10.1038/nature15725'
    Traceback (most recent call last):
    ...
    AssertionError: Required value "description" not found. Use helper=True or
    the --helper flag for assistance.

.. EXAMPLE-BLOCK-4-END

''', error=True)

    api.manager.set_required_archive_metadata({})


@pytest.mark.cli_snippets
def test_cli_snippet_5(setup, monkeypatch):

    runner, api, config_file, prefix = setup
    api.manager.set_required_archive_metadata({
        'description': 'Enter a description'})

    def get_description(*args, **kwargs):
        return "my_description"

    # override click.prompt
    monkeypatch.setattr('click.prompt', get_description)

    validate_command(setup, '''

.. EXAMPLE-BLOCK-5-START

.. code-block:: bash

    $ datafs create my_archive_name --helper
    created versioned archive <DataArchive local://my_archive_name>

.. EXAMPLE-BLOCK-5-END

''')

    api.delete_archive('my_archive_name')
