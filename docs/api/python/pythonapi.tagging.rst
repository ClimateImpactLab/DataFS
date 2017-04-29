.. _pythonapi-tagging:

================
Tagging Archives
================

You can tag archives from within python or using the :ref:`command line interface <cli-tagging>`.

View the source for the code samples on this page in :ref:`snippets-pythonapi-tagging`.

Tagging on archive creation
---------------------------

When creating archives, you can specify tags using the ``tags`` argument. Tags must be strings and will be coerced to lowercase as a standard. You can specify as many as you would like as elements in a list:

.. include:: ../../../examples/snippets/pythonapi_tagging.py
    :start-after: .. EXAMPLE-BLOCK-1-START
    :end-before: .. EXAMPLE-BLOCK-1-END

You can then search for archives that have these tags using the :py:meth:`~datafs.DataAPI.search` method:

.. include:: ../../../examples/snippets/pythonapi_tagging.py
    :start-after: .. EXAMPLE-BLOCK-2-START
    :end-before: .. EXAMPLE-BLOCK-2-END

Searching for multiple tags yields the set of archives that match all of the criteria:

.. include:: ../../../examples/snippets/pythonapi_tagging.py
    :start-after: .. EXAMPLE-BLOCK-3-START
    :end-before: .. EXAMPLE-BLOCK-3-END

Searches that include a set of tags not jointly found in any archives yield no results:

.. include:: ../../../examples/snippets/pythonapi_tagging.py
    :start-after: .. EXAMPLE-BLOCK-4-START
    :end-before: .. EXAMPLE-BLOCK-4-END

Viewing and modifying tags on existing archives
-----------------------------------------------

Tags can be listed using the :py:meth:`~datafs.core.data_archive.DataArchive.get_tags` method:

.. include:: ../../../examples/snippets/pythonapi_tagging.py
    :start-after: .. EXAMPLE-BLOCK-5-START
    :end-before: .. EXAMPLE-BLOCK-5-END

You can add tags to an archive using the :py:meth:`~datafs.core.data_archive.DataArchive.add_tags` method:

.. include:: ../../../examples/snippets/pythonapi_tagging.py
    :start-after: .. EXAMPLE-BLOCK-6-START
    :end-before: .. EXAMPLE-BLOCK-6-END


Removing tags from an archive
-----------------------------

Specific tags can be removed from an archive using the :py:meth:`~datafs.core.data_archive.DataArchive.delete_tags` method:

.. include:: ../../../examples/snippets/pythonapi_tagging.py
    :start-after: .. EXAMPLE-BLOCK-7-START
    :end-before: .. EXAMPLE-BLOCK-7-END


