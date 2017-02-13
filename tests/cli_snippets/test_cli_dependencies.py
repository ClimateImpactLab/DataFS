
import pytest
import os


@pytest.mark.examples
@pytest.mark.cli_snippets
def test_cli_dependencies_snippet_1(cli_validator):

    with open('arch.txt', 'w+') as f:
        f.write('contents depend on archive 2 v1.1')

    cli_validator(r'''

.. EXAMPLE-BLOCK-1-START

.. code-block:: bash

    $ datafs create my_archive
    created versioned archive <DataArchive local://my_archive>

    $ echo "contents depend on archive 2 v1.1" >> arch.txt # doctest: +SKIP

    $ datafs update my_archive arch.txt  --dependency "archive2==1.1" \
    >     --dependency "archive3" # doctest: +NORMALIZE_WHITESPACE
    uploaded data to <DataArchive local://my_archive>. new version 0.0.1
    created.

    $ datafs get_dependencies my_archive
    archive2==1.1
    archive3

.. EXAMPLE-BLOCK-1-END

''')

    os.remove('arch.txt')

    # Code snippet 2

    cli_validator('''

.. EXAMPLE-BLOCK-2-START

.. code-block:: bash

    $ datafs set_dependencies my_archive --dependency archive2==1.2

    $ datafs get_dependencies my_archive
    archive2==1.2

.. EXAMPLE-BLOCK-2-END

Example 2 teardown

.. code-block:: bash

    $ datafs delete my_archive
    deleted archive <DataArchive local://my_archive>

''')


@pytest.mark.examples
@pytest.mark.cli_snippets
def test_cli_dependencies_snippet_3(cli_validator):

    cli_validator('''

.. EXAMPLE-BLOCK-3-START

.. code-block:: bash

    $ datafs create my_archive --description 'my test archive'
    created versioned archive <DataArchive local://my_archive>

.. EXAMPLE-BLOCK-3-END

cleanup:

.. code-block:: bash

    $ datafs delete my_archive
    deleted archive <DataArchive local://my_archive>

''')


@pytest.mark.examples
@pytest.mark.cli_snippets
def test_cli_dependencies_snippet_4(cli_validator_with_description):

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
def test_cli_dependencies_snippet_5(
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
