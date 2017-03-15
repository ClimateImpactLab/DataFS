.. _cli-finding-archives:

================
Finding Archives
================




In this section we'll take a look at finding archives via the command line. 

You can find archives from the command line interface or from :ref:`python <pythonapi-finding-archives>`. This documentation mirrors the python documentation. 


Using ``listdir``
~~~~~~~~~~~~~~~~~

In our database we have many archives. We know that ``impactlab`` is a top-level namespace in our database. Let's have a look. 

.. include:: ../tests/cli_snippets/test_cli_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-1-START
    :end-before: .. EXAMPLE-BLOCK-1-END


Ok. We see that ``labor``, ``climate``, ``mortality`` and ``conflict`` are all namespaces below ``impactlab``. Lets have a look at ``conflict``. 

.. include:: ../tests/cli_snippets/test_cli_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-2-START
    :end-before: .. EXAMPLE-BLOCK-2-END

Let's see what is in ``impactlab/conflict/global``. 

.. include:: ../tests/cli_snippets/test_cli_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-3-START
    :end-before: .. EXAMPLE-BLOCK-3-END

We can see that there is currently only version ``0.0.1`` of ``conflict_global_daily.csv``


Using ``filter``
~~~~~~~~~~~~~~~~~

DataFS lets you filter so you can limit the search space on archive names. At the command line, you can use the ``prefix``, ``path``, ``str``, and ``regex`` pattern options to filter archives.
Let's look at using the ``prefix`` ``project1_variable1_`` which corresponds to the ``prefix`` option, the beginning string of a set of archive names. 


.. include:: ../tests/cli_snippets/test_cli_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-4-START
    :end-before: .. EXAMPLE-BLOCK-4-END

We can also filter on ``path``. In this case we want to filter all NetCDF files that match a specific pattern. We need to set our ``engine`` value to ``path`` and put in our search pattern.

.. include:: ../tests/cli_snippets/test_cli_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-5-START
    :end-before: .. EXAMPLE-BLOCK-5-END

We can also filter archives with archive names containing a specific string by setting ``engine`` to ``str``. In this example we want all archives with the string ``variable2``. 

.. include:: ../tests/cli_snippets/test_cli_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-6-START
    :end-before: .. EXAMPLE-BLOCK-6-END




Using ``search``
~~~~~~~~~~~~~~~~

DataFS ``search`` capabilites are enabled via tagging of archives. The arguments of the ``search`` command are tags associated with a given archive. If archives are not tagged, they cannot be searched. 

Our archives have been tagged with ``team1``, ``team2``, or ``team3`` Let's search for some archives with tag ``team3``.

.. include:: ../tests/cli_snippets/test_cli_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-7-START
    :end-before: .. EXAMPLE-BLOCK-7-END


Let's use ``get_tags`` to have a look at one of our archives' tags.

.. include:: ../tests/cli_snippets/test_cli_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-8-START
    :end-before: .. EXAMPLE-BLOCK-8-END

We can see that indeed it has been tagged with ``team3``. 


For completeness, let's have a look at archives with tag of ``team1``.   

.. include:: ../tests/cli_snippets/test_cli_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-9-START
    :end-before: .. EXAMPLE-BLOCK-9-END

And now let's have a look at one of them to see what tags are associated with it.


.. include:: ../tests/cli_snippets/test_cli_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-10-START
    :end-before: .. EXAMPLE-BLOCK-10-END

We can see clearly that our archive has been tagged with ``team1``. 



If you find bugs or have suggestions to improve this documentation, please file an issue and make a pull request.  


