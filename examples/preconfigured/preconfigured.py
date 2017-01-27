'''

This tutorial walks through the process of creating the specification files
and setting up resources for use on a large team. It assumes a basic level of
familiarity with the purpose of DataFS, and also requires administrative access
to any resources you'd like to use, such as AWS.

Set up a connection to AWS
~~~~~~~~~~~~~~~~~~~~~~~~~~

To use AWS resources, you'll need credentials. These are most easily specified
in a credentials file.

We've provided a sample file
:download:`here <../examples/preconfigured/credentials>`:

.. literalinclude:: ../examples/preconfigured/credentials
    :linenos:

This file is located ``~/.aws/credentials`` by default, but we'll tell AWS how
to find it locally using an environment variable for the purpose of this
example:

.. code-block:: python

    >>> import os
    >>>
    >>> # Change this to wherever your credentials file is:
    ... credentials_file_path = os.path.join(
    ...     os.path.dirname(__file__),
    ...     'credentials')
    ...
    >>> os.environ['AWS_SHARED_CREDENTIALS_FILE'] = credentials_file_path


Configure DataFS for your organization/use
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that you have a connection to AWS, you can specify how you want DataFS to
work. DataFS borrows the idea of profiles, allowing you to have multiple
pre-configured file managers at once.

We'll set up a test profile called "example"
:download:`here <../examples/preconfigured/.datafs.yml>`:

.. literalinclude:: ../examples/preconfigured/.datafs.yml
    :language: yaml
    :linenos:


Set up team managers and services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make sure that the directories, buckets, etc. that your services are connecting
to exist:

.. code-block:: python

    >>> if not os.path.isdir('example_data_dir'):
    ...     os.makedirs('example_data_dir')


Now, boot up an API and create the archive table on your manager that
corresponds to the one specified in your

.. code-block:: python

    >>> import datafs
    >>> api = datafs.get_api(
    ...     profile='example',
    ...     config_file='examples/preconfigured/.datafs.yml')
    >>>
    >>> api.manager.create_archive_table('my-test-data')


Finally, we'll set some basic reporting requirements that will be enforced when
users interact with the data.


We can require user information when writing/updating an archive.
:py:meth:`~datafs.managers.BaseDataManager.set_required_user_config` allows
administrators to set user configuration requirements and provide a prompt to
help users:

.. code-block:: python

    >>> api.manager.set_required_user_config({
    ...     'username': 'your full name',
    ...     'contact': 'your email address'})

Similarly,
:py:meth:`~datafs.managers.BaseDataManager.set_required_archive_metadata`
sets the metadata that is required for each archive:

    >>> api.manager.set_required_archive_metadata({
    ...     'description': 'a long description of the archive'})

Attempts by users to create/update archives without these attributes will now
fail.


Using the API
~~~~~~~~~~~~~

At this point, any users with properly specified credentials and config files
can use the data api.

From within python:

.. code-block:: python

    >>> import datafs
    >>> api = datafs.get_api(
    ...     profile='example',
    ...     config_file='examples/preconfigured/.datafs.yml')
    >>>
    >>> archive = api.create(
    ...     'archive1',
    ...     authority_name='local',
    ...     metadata = {'description': 'my new archive'})

Note that the metadata requirements you specified are enforced. If a user tries
to skip the description, an error is raised and the archive is not created:

.. code-block:: python

    >>> archive = api.create(
    ...     'archive2',
    ...     authority_name='local')
    ...  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    AssertionError: Required value "description" not found. Use helper=True or
    the --helper flag for assistance.
    >>>
    >>> print(next(api.filter()))
    archive1


Setting User Permissions
~~~~~~~~~~~~~~~~~~~~~~~~

Users can be managed using policies on AWS's admin console. An example policy
allowing users to create, update, and find archives without allowing
them to delete archives or to modify the required metadata specification is
provided
:download:`here <../examples/preconfigured/DynamoDB_user_policy.json>`:


.. literalinclude:: ../examples/preconfigured/DynamoDB_user_policy.json
    :language: json
    :linenos:


A user with AWS access keys using this policy will see an AccessDeniedException
when attempting to take restricted actions:

.. code-block:: python

    >>> import datafs
    >>> api = datafs.get_api(profile='user') # doctest: +SKIP
    >>>
    >>> archive = api.get_archive('archive1')
    >>>
    >>> archive.delete() # doctest: +SKIP
    Traceback (most recent call last):
    ...
    botocore.exceptions.ClientError: An error occurred (AccessDeniedException)
    when calling the DeleteItem operation: ...


Teardown
~~~~~~~~

A user with full privileges can completely remove archives and manager tables:

.. code-block:: python

    >>> api.delete_archive('archive1')
    >>> api.manager.delete_table('my-test-data')

'''
