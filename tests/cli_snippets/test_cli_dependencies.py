
from tests.cli_snippets.resources import validate_command
import pytest
import os


@pytest.mark.cli_snippets
def test_cli_snippet_1(cli_setup):

    runner, api, config_file, prefix = cli_setup

    with open('arch.txt', 'w+') as f:
        f.write('contents depend on archive 2 v1.1')

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-1-START

.. code-block:: bash

    $ datafs create my_archive
    created versioned archive <DataArchive local://my_archive>

    $ echo "contents depend on archive 2 v1.1" >> arch.txt
    
    $ datafs update my_archive arch.txt  --dependency "archive2==1.1" --dependency "archive3"
    uploaded data to <DataArchive local://my_archive>. new version 0.0.1 created.

    $ datafs get_dependencies my_archive
    archive2==1.1
    archive3

.. EXAMPLE-BLOCK-1-END

''')

    os.remove('arch.txt')

    # Code snippet 2

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-2-START

.. code-block:: bash

    $ datafs set_dependencies my_archive --dependency archive2==1.2

    $ datafs get_dependencies my_archive
    archive2==1.2

.. EXAMPLE-BLOCK-2-END

''')

    api.delete_archive('my_archive')



@pytest.mark.cli_snippets
def test_cli_snippet_3(cli_setup):

    runner, api, config_file, prefix = cli_setup

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-3-START

.. code-block:: bash

    $ datafs create my_archive --description 'my test archive'
    created versioned archive <DataArchive local://my_archive>

.. EXAMPLE-BLOCK-3-END

''')

    api.delete_archive('my_archive')


@pytest.mark.cli_snippets
def test_cli_snippet_4(cli_setup):

    runner, api, config_file, prefix = cli_setup

    api.manager.set_required_archive_metadata({
        'description': 'Archive description'})

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-4-START

.. code-block:: bash

    $ datafs create my_archive --doi '10.1038/nature15725' --author "burke"
    Traceback (most recent call last):
    ...
    AssertionError: Required value "description" not found. Use helper=True or
    the --helper flag for assistance.

.. EXAMPLE-BLOCK-4-END

''', error=True)

    api.manager.set_required_archive_metadata({})


@pytest.mark.cli_snippets
def test_cli_snippet_5(cli_setup, monkeypatch):

    runner, api, config_file, prefix = cli_setup
    api.manager.set_required_archive_metadata({
        'description': 'Enter a description'})

    def get_description(*args, **kwargs):
        return "my_description"

    # override click.prompt
    monkeypatch.setattr('click.prompt', get_description)

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-5-START

.. code-block:: bash

    $ datafs create my_archive --helper
    created versioned archive <DataArchive local://my_archive>

.. EXAMPLE-BLOCK-5-END

''')

    api.delete_archive('my_archive')
