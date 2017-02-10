
from tests.cli_snippets.resources import validate_command
import pytest
import os


@pytest.mark.cli_snippets
def test_cli_snippets(cli_setup):

    # snippet 1

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-1-START

.. code-block:: bash

    $ datafs filter

.. EXAMPLE-BLOCK-1-END

''')

    # snippet 2

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-2-START

.. code-block:: bash

    $ datafs create my_archive 
    created versioned archive <DataArchive local://my_archive>

.. EXAMPLE-BLOCK-2-END

''')

    # snippet 3

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-3-START

.. code-block:: bash

    $ datafs filter
    my_archive

.. EXAMPLE-BLOCK-3-END

''')

    # snippet 4

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-4-START

.. code-block:: bash

    $ datafs update my_archive --string 'barba crescit caput nescit'
    uploaded data to <DataArchive local://my_archive>. new version 0.0.1 created.

.. EXAMPLE-BLOCK-4-END

''')

    # snippet 5

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-5-START

.. code-block:: bash

    $ datafs download my_archive '~/data/my_archive.txt'
    downloaded  v0.0.1 to /Users/data/my_archive.txt

.. EXAMPLE-BLOCK-5-END

''')

    # snippet 6

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-6-START

.. code-block:: bash
    
    $ cat ~/data/my_archive.txt
    barba crescit caput nescit

.. EXAMPLE-BLOCK-6-END

''')

    # snippet 7

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-7-START

.. code-block:: bash

    $ datafs update my_archive ~/data/my_archive.txt
    uploaded data to <DataArchive local://my_archive>. version bumped 0.0.1 --> 0.0.2

.. EXAMPLE-BLOCK-7-END

''')

    # snippet 8

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-8-START

.. code-block:: bash

    $ datafs download my_archive ~/data/my_archive_placeholder.txt
    downloaded  v0.0.2 to /Users/data/my_archive_placeholder.txt
    
    $ cat ~/data/my_archive_placeholder.txt
    barba crescit caput nescit
    luctuat nec mergitur

.. EXAMPLE-BLOCK-8-END

''')

    _, api, _, _ = cli_setup

    api.delete_archive('my_archive')
