
import pytest
import os


@pytest.mark.examples
@pytest.mark.cli_snippets
def test_cli_io_snippets(cli_validator):

    # snippet 1

    cli_validator(r'''

.. EXAMPLE-BLOCK-1-START

.. code-block:: bash

    $ datafs filter

.. EXAMPLE-BLOCK-1-END


Snippet 2

.. EXAMPLE-BLOCK-2-START

.. code-block:: bash

    $ datafs create my_archive
    created versioned archive <DataArchive local://my_archive>

.. EXAMPLE-BLOCK-2-END


Snippet 3

.. EXAMPLE-BLOCK-3-START

.. code-block:: bash

    $ datafs filter
    my_archive

.. EXAMPLE-BLOCK-3-END


Snippet 4

.. EXAMPLE-BLOCK-4-START

.. code-block:: bash

    $ datafs update my_archive \
    >   --string 'barba crescit caput nescit' # doctest: +NORMALIZE_WHITESPACE
    uploaded data to <DataArchive local://my_archive>. new version 0.0.1
    created.

.. EXAMPLE-BLOCK-4-END


Snippet 5

.. EXAMPLE-BLOCK-5-START

.. code-block:: bash

    $ datafs download my_archive 'my_archive.txt'
    downloaded v0.0.1 to my_archive.txt

.. EXAMPLE-BLOCK-5-END


Snippet 6

.. EXAMPLE-BLOCK-6-START

.. code-block:: bash

    $ cat my_archive.txt
    barba crescit caput nescit

.. EXAMPLE-BLOCK-6-END

''')

    with open('my_archive.txt', 'a') as f:
        f.write('\nluctuat nec mergitur\n')

    cli_validator(r'''

Snippet 7

Update the file

.. EXAMPLE-BLOCK-7-START

.. code-block:: bash

    $ datafs update my_archive my_archive.txt # doctest: +NORMALIZE_WHITESPACE
    uploaded data to <DataArchive local://my_archive>. version bumped 0.0.1 -->
    0.0.2.

.. EXAMPLE-BLOCK-7-END


Snippet 8

.. EXAMPLE-BLOCK-8-START

.. code-block:: bash

    $ datafs download my_archive my_archive_placeholder.txt
    downloaded v0.0.2 to my_archive_placeholder.txt

    $ cat my_archive_placeholder.txt # doctest: +NORMALIZE_WHITESPACE
    barba crescit caput nescit
    luctuat nec mergitur

.. EXAMPLE-BLOCK-8-END

Teardown

.. code-block:: bash

    $ datafs delete my_archive
    deleted archive <DataArchive local://my_archive>

''')

    os.remove('my_archive.txt')
    os.remove('my_archive_placeholder.txt')
