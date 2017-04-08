
import pytest


@pytest.mark.examples
@pytest.mark.cli_snippets
def test_cli_creating_archives_snippet_1(cli_validator):

    cli_validator('''

.. EXAMPLE-BLOCK-1-START

.. code-block:: bash

    $ datafs create my_archive
    created versioned archive <DataArchive local://my_archive>

.. EXAMPLE-BLOCK-1-END

Snippet 1 teardown

.. code-block:: bash

    $ datafs delete my_archive
    deleted archive <DataArchive local://my_archive>

''')


@pytest.mark.examples
@pytest.mark.cli_snippets
def test_cli_creating_archives_snippet_2(cli_validator_dual_auth):

    cli_validator_dual_auth('''

.. EXAMPLE-BLOCK-2-START

.. code-block:: bash

    $ datafs create my_archive --authority_name "my_authority"
    created versioned archive <DataArchive my_authority://my_archive>

.. EXAMPLE-BLOCK-2-END

Snippet 2 teardown

.. code-block:: bash

    $ datafs delete my_archive
    deleted archive <DataArchive my_authority://my_archive>

''')


@pytest.mark.examples
@pytest.mark.cli_snippets
def test_cli_creating_archives_snippet_3(cli_validator):

    cli_validator('''

.. EXAMPLE-BLOCK-3-START

.. code-block:: bash

    $ datafs create my_archive --description 'my test archive'
    created versioned archive <DataArchive local://my_archive>

.. EXAMPLE-BLOCK-3-END

Snippet 3 teardown

.. code-block:: bash

    $ datafs delete my_archive
    deleted archive <DataArchive local://my_archive>

''')


@pytest.mark.examples
@pytest.mark.cli_snippets
def test_cli_creating_archives_snippet_4(cli_validator_with_description):

    cli_validator_with_description(r'''

.. EXAMPLE-BLOCK-4-START

.. code-block:: bash

    $ datafs create my_archive --doi '10.1038/nature15725' \
    >     --author "burke" # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    AssertionError: Required value "description" not found. Use helper=True or
    the --helper flag for assistance.

.. EXAMPLE-BLOCK-4-END

''')


@pytest.mark.examples
@pytest.mark.cli_snippets
def test_cli_creating_archives_snippet_5(
        cli_validator_with_description,
        monkeypatch):

    def get_description(*args, **kwargs):
        return "my_description"

    # override click.prompt
    monkeypatch.setattr('click.prompt', get_description)

    cli_validator_with_description('''

.. EXAMPLE-BLOCK-5-START

.. code-block:: bash

    $ datafs create my_archive --helper
    created versioned archive <DataArchive local://my_archive>

.. EXAMPLE-BLOCK-5-END

Snippet 5 teardown

.. code-block:: bash

    $ datafs delete my_archive
    deleted archive <DataArchive local://my_archive>

''')
