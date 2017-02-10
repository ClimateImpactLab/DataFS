
from tests.cli_snippets.resources import validate_command
import pytest
import os


@pytest.mark.cli_snippets
def test_cli_snippet_1(cli_setup):

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-1-START

.. code-block:: bash

    $ datafs filter

.. EXAMPLE-BLOCK-1-END

''')


@pytest.mark.cli_snippets
def test_cli_snippet_2(cli_setup):

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-2-START

.. code-block:: bash

    $ datafs create sample_archive 
    created versioned archive <DataArchive osfs://sample_archive>

.. EXAMPLE-BLOCK-2-END

''')



@pytest.mark.cli_snippets
def test_cli_snippet_3(cli_setup):

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-3-START

.. code-block:: bash

    $ datafs filter
    sample_archive

.. EXAMPLE-BLOCK-3-END

''')


@pytest.mark.cli_snippets
def test_cli_snippet_4(cli_setup):

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-4-START

.. code-block:: bash

    datafs update sample_archive --string 'barba crescit caput nescit'
    uploaded data to <DataArchive osfs://sample_archive>. new version 0.0.1 created.

.. EXAMPLE-BLOCK-4-END

''')


@pytest.mark.cli_snippets
def test_cli_snippet_5(cli_setup, monkeypatch):

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-5-START

.. code-block:: bash

    datafs download sample_archive '~/data/sample_archive.txt'
    downloaded  v0.0.1 to /Users/data/sample_archive.txt

.. EXAMPLE-BLOCK-5-END

''')


@pytest.mark.cli_snippets
def test_cli_snippet_6(cli_setup, monkeypatch):

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-6-START

.. code-block:: bash
    
    cat ~/data/sample_archive.txt
    barba crescit caput nescit

.. EXAMPLE-BLOCK-6-END

''')


@pytest.mark.cli_snippets
def test_cli_snippet_7(cli_setup, monkeypatch):

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-7-START

.. code-block:: bash

    datafs update sample_archive ~/data/sample_archive.txt
    uploaded data to <DataArchive osfs://sample_archive>. version bumped 0.0.1 --> 0.0.2

.. EXAMPLE-BLOCK-7-END

''')


@pytest.mark.cli_snippets
def test_cli_snippet_8(cli_setup, monkeypatch):

    validate_command(cli_setup, '''

.. EXAMPLE-BLOCK-8-START

.. code-block:: bash

    datafs download sample_archive ~/data/sample_archive_placeholder.txt
    downloaded  v0.0.2 to /Users/data/sample_archive_placeholder.txt
    
    cat ~/data/sample_archive_placeholder.txt
    barba crescit caput nescit
    luctuat nec mergitur

.. EXAMPLE-BLOCK-8-END

''')

