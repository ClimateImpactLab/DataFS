
from tests.cli_snippets.resources import validate_command
import pytest
import os


@pytest.mark.cli_snippets
def test_cli_snippet_1(cli_setup):

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-1-START

.. code-block:: bash

    $ datafs create my_archive metadata 'useful metadata'
    created versioned archive <DataArchive local://my_archive>

.. EXAMPLE-BLOCK-1-END

''')


@pytest.mark.cli_snippets
def test_cli_snippet_2(cli_setup):

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-2-START

.. code-block:: bash

    $ datafs update my_archive --string 'barba crescit caput nescit'
    uploaded data to <DataArchive local://my_archive>. new version 0.0.1 created.

.. EXAMPLE-BLOCK-2-END

''')



@pytest.mark.cli_snippets
def test_cli_snippet_3(cli_setup):

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-3-START

.. code-block:: bash

    $ datafs update my_archive --bumpversion patch --string 'Aliquando et insanire iucundum est'
    uploaded data to <DataArchive local://my_archive>. version bumped 0.0.1 --> 0.0.2

    $ datafs update my_archive --bumpversion minor --string 'animum debes mutare non caelum'
    uploaded data to <DataArchive local://sample_arch>. version bumped 0.0.2 --> 0.1.

.. EXAMPLE-BLOCK-3-END

''')


@pytest.mark.cli_snippets
def test_cli_snippet_4(cli_setup):

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-4-START

.. code-block:: bash

    $ datafs versions my_archive 
    ['0.0.1', '0.0.2', '0.1']

.. EXAMPLE-BLOCK-4-END

''')


@pytest.mark.cli_snippets
def test_cli_snippet_5(cli_setup, monkeypatch):

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-5-START

.. code-block:: bash

    $ datafs download my_archive my_archive_versioned.txt --version 0.0.2
    downloaded v.0.0.2 to my_archive_versioned.txt

.. EXAMPLE-BLOCK-5-END

''')
