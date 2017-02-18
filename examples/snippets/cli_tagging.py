r'''
.. _snippets-cli-tagging:

Command Line Interface: Tagging
===============================

This is the tested source code for the snippets used in :ref:`cli-tagging`. The
config file we're using in this example can be downloaded
:download:`here <../examples/snippets/resources/datafs.yml>`.

Example 1
---------

Displayed example 1 code:

.. EXAMPLE-BLOCK-1-START

.. code-block:: bash

    $ datafs create archive1 --tag "foo" --tag "bar" --description \
    >     "tag test 1 has bar"
    created versioned archive <DataArchive local://archive1>

    $ datafs create archive2 --tag "foo" --tag "baz" --description \
    >     "tag test 2 has baz"
    created versioned archive <DataArchive local://archive2>

.. EXAMPLE-BLOCK-1-END


Example 2
---------

.. EXAMPLE-BLOCK-2-START

.. code-block:: bash

    $ datafs search bar
    archive1

    $ datafs search baz
    archive2

    $ datafs search foo
    archive1
    archive2

.. EXAMPLE-BLOCK-2-END


Example 3
---------

.. EXAMPLE-BLOCK-3-START

.. code-block:: bash

    $ datafs create archive3 --tag "foo" --tag "bar" --tag "baz" \
    >     --description 'tag test 3 has all the tags!'
    created versioned archive <DataArchive local://archive3>

    $ datafs search bar foo
    archive1
    archive3

    $ datafs search bar foo baz
    archive3

.. EXAMPLE-BLOCK-3-END

Example 4
---------

.. EXAMPLE-BLOCK-4-START

.. code-block:: bash

    $ datafs search qux

    $ datafs search foo qux


.. EXAMPLE-BLOCK-4-END


Example 5
---------

.. EXAMPLE-BLOCK-5-START

.. code-block:: bash

    $ datafs get_tags archive1
    foo bar


.. EXAMPLE-BLOCK-5-END


Example 6
---------

.. EXAMPLE-BLOCK-6-START

.. code-block:: bash

    $ datafs add_tags archive1 qux

    $ datafs search foo qux
    archive1


.. EXAMPLE-BLOCK-6-END


Example 7
---------

.. EXAMPLE-BLOCK-7-START

.. code-block:: bash

    $ datafs delete_tags archive1 foo bar

    $ datafs search foo bar
    archive3


.. EXAMPLE-BLOCK-7-END


Teardown
--------

.. code-block:: bash

    $ datafs delete archive1
    deleted archive <DataArchive local://archive1>

    $ datafs delete archive2
    deleted archive <DataArchive local://archive2>

    $ datafs delete archive3
    deleted archive <DataArchive local://archive3>

'''
