.. _cli-versioning:

=================
Tracking Versions
=================


In this section we'll have a look at the archive versioning options available through the command line. 

We'll assume we have our api configured and that our manager and authority is already set-up. We go ahead and creat our sample archive again to demonstrate how versions are managed.

.. include:: ../../../tests/cli_snippets/test_cli_versioning.py
    :start-after: .. EXAMPLE-BLOCK-1-START
    :end-before: .. EXAMPLE-BLOCK-1-END


So now we have our archive being tracked by manager. 


.. include:: ../../../tests/cli_snippets/test_cli_versioning.py
    :start-after: .. EXAMPLE-BLOCK-2-START
    :end-before: .. EXAMPLE-BLOCK-2-END


Explicit Versioning
-------------------

As we learned in our section on writing and reading archives, the version is set to 0.0.1 on creation by default. 
If you wanted to specify a prerelease or a minor release you would do either of the following


.. include:: ../../../tests/cli_snippets/test_cli_versioning.py
    :start-after: .. EXAMPLE-BLOCK-3-START
    :end-before: .. EXAMPLE-BLOCK-3-END


Get Version History
-------------------

What if we want to view our versions? 

.. include:: ../../../tests/cli_snippets/test_cli_versioning.py
    :start-after: .. EXAMPLE-BLOCK-4-START
    :end-before: .. EXAMPLE-BLOCK-4-END


Downloading Specific Versions
-----------------------------

How can we get a specific version?


.. include:: ../../../tests/cli_snippets/test_cli_versioning.py
    :start-after: .. EXAMPLE-BLOCK-5-START
    :end-before: .. EXAMPLE-BLOCK-5-END

