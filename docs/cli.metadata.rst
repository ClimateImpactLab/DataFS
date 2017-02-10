.. _cli-metadata:

=================
Managing Metadata
=================



In this section we'll take a look at how to access archive metadata from the command line. There is also a
:ref:`python <pythonapi-metadata>` version. 

Viewing Metadata
----------------


We'll keep working with our ``sample_archive`` that we created earlier. Right now we'll take a look at our metadata. Depending 

.. include:: ../tests/cli_snippets/test_cli_metadata.py
    :start-after: .. EXAMPLE-BLOCK-1-START
    :end-before: .. EXAMPLE-BLOCK-1-END

Let's say that we want to change one and add another entry. How can we do this?


Updating Metadata
-----------------


.. include:: ../tests/cli_snippets/test_cli_metadata.py
    :start-after: .. EXAMPLE-BLOCK-2-START
    :end-before: .. EXAMPLE-BLOCK-2-END



We'll need to read the metadata again to check to see if we succeeded


.. include:: ../tests/cli_snippets/test_cli_metadata.py
    :start-after: .. EXAMPLE-BLOCK-3-START
    :end-before: .. EXAMPLE-BLOCK-3-END

Great!

It should be noted that the command line tool does not deal with whitespaces well so you'll need to wrap text in quotes if it refers to a single entry. The command line tool is looking for key value pairs. To preserve this symmetry you'll need to use quotations around some entries. 


