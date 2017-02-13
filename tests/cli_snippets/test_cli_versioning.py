
import pytest
import os


@pytest.mark.examples
@pytest.mark.cli_snippets
def test_cli_versioning_snippets(cli_validator):

    cli_validator(r'''

.. EXAMPLE-BLOCK-1-START

.. code-block:: bash

    $ datafs create my_archive \
    >   --my_metadata_field 'useful metadata'
    created versioned archive <DataArchive local://my_archive>

.. EXAMPLE-BLOCK-1-END


Snippet 2

.. EXAMPLE-BLOCK-2-START

.. code-block:: bash

    $ datafs update my_archive --string \
    >     'barba crescit caput nescit' # doctest: +NORMALIZE_WHITESPACE
    uploaded data to <DataArchive local://my_archive>. new version 0.0.1
    created.

.. EXAMPLE-BLOCK-2-END


Snippet 3

.. EXAMPLE-BLOCK-3-START

.. code-block:: bash

    $ datafs update my_archive --bumpversion patch --string \
    >     'Aliquando et insanire iucundum est' # doctest: +NORMALIZE_WHITESPACE
    uploaded data to <DataArchive local://my_archive>. version bumped 0.0.1 -->
    0.0.2.

    $ datafs update my_archive --bumpversion minor --string \
    >     'animum debes mutare non caelum' # doctest: +NORMALIZE_WHITESPACE
    uploaded data to <DataArchive local://my_archive>. version bumped 0.0.2 -->
    0.1.

.. EXAMPLE-BLOCK-3-END


Snippet 4

.. EXAMPLE-BLOCK-4-START

.. code-block:: bash

    $ datafs versions my_archive
    ['0.0.1', '0.0.2', '0.1']

.. EXAMPLE-BLOCK-4-END


Snippet 5

.. EXAMPLE-BLOCK-5-START

.. code-block:: bash

    $ datafs download my_archive my_archive_versioned.txt --version 0.0.2
    downloaded v0.0.2 to my_archive_versioned.txt

.. EXAMPLE-BLOCK-5-END

cleanup:

.. code-block:: bash

    $ datafs delete my_archive
    deleted archive <DataArchive local://my_archive>

''')

    os.remove('my_archive_versioned.txt')
