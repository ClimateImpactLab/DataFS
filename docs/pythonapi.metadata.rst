.. _pythonapi-metadata:

=================
Managing Metadata
=================


Metadata management is one of the core components of DataFS. Metadata is managed at the Archive level and the version level. This documentation will refer to the Archive level metadata. 

View the source for the code samples on this page in :ref:`snippets-pythonapi-metadata`


We'll assume that your manager and authority have been set up already. Depending on usage, metadata requirements can be enforced and archive creation will be possible only with inclusion of the required metadata. 

.. include:: ../examples/snippets/pythonapi_metadata.py
    :start-after: .. EXAMPLE-BLOCK-1-START
    :end-before: .. EXAMPLE-BLOCK-1-END

Let's check to see if we have any other archives. It looks like we only have our ``sample_archive``. 

.. include:: ../examples/snippets/pythonapi_metadata.py
    :start-after: .. EXAMPLE-BLOCK-2-START
    :end-before: .. EXAMPLE-BLOCK-2-END

Nope just this one. So let's have a look at the metadata using :py:meth:`~datafs.core.data_archive.DataArchive.get_metadata`. 

.. include:: ../examples/snippets/pythonapi_metadata.py
    :start-after: .. EXAMPLE-BLOCK-3-START
    :end-before: .. EXAMPLE-BLOCK-3-END

Let's say you later on realize that you want to add another field to the archive metadata and that you also want to update on of the required fields. The archive metadata is modified in place and so you'll be able to do both at the same time with :py:meth:`~datafs.core.data_archive.DataArchive.update_metadata`

.. include:: ../examples/snippets/pythonapi_metadata.py
    :start-after: .. EXAMPLE-BLOCK-4-START
    :end-before: .. EXAMPLE-BLOCK-4-END

As you can see the source was updated and the ``related_links`` key and value were added.

.. include:: ../examples/snippets/pythonapi_metadata.py
    :start-after: .. EXAMPLE-BLOCK-5-START
    :end-before: .. EXAMPLE-BLOCK-5-END

As long as a particular metadata key-value pair is not a required field, you can remove it. If you want to remove a particular key-value pair from the archive metadata, set the value to None:

.. include:: ../examples/snippets/pythonapi_metadata.py
    :start-after: .. EXAMPLE-BLOCK-6-START
    :end-before: .. EXAMPLE-BLOCK-6-END


Now our ``related_links`` key-value pair has been removed. To edit the required metadata fields, please 
see :ref:`admin`. 

