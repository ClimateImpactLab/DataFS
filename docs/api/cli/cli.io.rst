.. _cli-io:

=========================
Reading and Writing Files
=========================



Reading from and writing to files is straight forward in DataFS. In this section we'll cover the command-line implementation of this. The :ref:`python <pythonapi-io>` implementation is also available.

We'll assume you have your api configured with a manager and an authority. Check the :ref:`configure <configure>` documentation for more information on how to set up DataFS.


Listing Archives
----------------

If I want to first check to see if I have any archives I can use the `filter` command. Here we see we don't currently have any archives

.. include:: ../../../tests/cli_snippets/test_cli_io.py
    :start-after: .. EXAMPLE-BLOCK-1-START
    :end-before: .. EXAMPLE-BLOCK-1-END

So let's create an archive so we have something to work with. 

.. include:: ../../../tests/cli_snippets/test_cli_io.py
    :start-after: .. EXAMPLE-BLOCK-2-START
    :end-before: .. EXAMPLE-BLOCK-2-END

Now when we list we see our archive. Great!

.. include:: ../../../tests/cli_snippets/test_cli_io.py
    :start-after: .. EXAMPLE-BLOCK-3-START
    :end-before: .. EXAMPLE-BLOCK-3-END


Writing to Archives
-------------------

This time we will simply demonstrate how you can 

.. include:: ../../../tests/cli_snippets/test_cli_io.py
    :start-after: .. EXAMPLE-BLOCK-4-START
    :end-before: .. EXAMPLE-BLOCK-4-END

Great! 


Reading from Archives
---------------------

.. include:: ../../../tests/cli_snippets/test_cli_io.py
    :start-after: .. EXAMPLE-BLOCK-5-START
    :end-before: .. EXAMPLE-BLOCK-5-END

Now let's read this to make sure we got what we want

.. include:: ../../../tests/cli_snippets/test_cli_io.py
    :start-after: .. EXAMPLE-BLOCK-6-START
    :end-before: .. EXAMPLE-BLOCK-6-END


Writing to Archives with Filepaths
----------------------------------

Let's say we made some major edits to our sample_archive locally and we want to update them in the manager and at our authority. We can update the same as before but this time we'll add the filepath that points to our file.

.. include:: ../../../tests/cli_snippets/test_cli_io.py
    :start-after: .. EXAMPLE-BLOCK-7-START
    :end-before: .. EXAMPLE-BLOCK-7-END

And now to read this file, let's download to a different spot and read from there.

.. include:: ../../../tests/cli_snippets/test_cli_io.py
    :start-after: .. EXAMPLE-BLOCK-8-START
    :end-before: .. EXAMPLE-BLOCK-8-END

We can see that our updates have been added and that they are reflected in a new version number. 
