
.. _configure.cache:

=====================
Caching Files Locally
=====================

One of the primary motivations for DataFS is the ability to have access to large numbers of versioned file systems in a distributed, heterogenous computing environment. This is achieved through explicit caching.

Caching in datafs is highly configurable, and is specific to each DataAPI instance, so you can have one profile which caches all archives locally and another which accesses files only through remote connections. This behavior is controlled through the use of API-specific cache policies.


Configuring a cache consists of two actions - :ref:`attaching a cache <configure.cache.setup>` and :ref:`assigning a policy <configure.cache.policy>`.

.. _configure.cache.setup:

Setting up a cache
------------------

Types of caches
~~~~~~~~~~~~~~~

As with :ref:`authorities <configure.authorities>`, caches can technically be any pyfilesystem fs, though they are typically a local directory or a network drive. But anything that would be faster for read/write than the authorities is a valid cache.


Attaching through the Python API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. example code



Using a configuration file
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. example code



.. _configure.cache.policy:

Cache policies
--------------

The cache policy determines whether and how DataFS will cache files on the cache you configure. *By default, the cache policy is set to* ``never`` *so even if a cache is present it will not be used until a cache policy is set!*


Available cache policies
~~~~~~~~~~~~~~~~~~~~~~~~

The cache policy can be set to one of the following values:

* ``always`` will retain any accessed version of every archive
* ``latest`` will retain the latest version of an archive
* ``mru``, or *most recently used*, will retain the last used version of an archive
* ``never`` (default) will not cache any files


Cache policy behavior
~~~~~~~~~~~~~~~~~~~~~


As a general rule, operations should cache exactly what you expect, and no more. Versions not clearly indicated by the state will be removed from the cache when encountered.

More explicitly, cache policies have the following behavior when reading and writing archives:

+--------------+---------+---------------------+-----------------------+
|              | Action                                                |
+              +---------+---------------------+-----------------------+
|              |         | Read with mode      | Read with mode ``r+`` |
| Cache Policy | Write   | ``r`` or Download   | or Get\_local\_path   |
+==============+=========+=====================+=======================+
| ``'always'`` | Cache all files encountered                           |
+--------------+---------+---------------------+-----------------------+
|              |         |                     | Cache if latest.      |
| ``'latest'`` |         | Cache if latest     | Replace with new      |
|              |         |                     | version if file is    |
|              | Cache   |                     | written.              |
+--------------+ new     +---------------------+-----------------------+
|              | version |                     | Cache. Replace with   |
| ``'mru'``    |         | Cache               | new version if file   |
|              |         |                     | is written.           |
+--------------+---------+---------------------+-----------------------+
| ``'never'``  | Do not cache. Delete all files encountered.           |
+--------------+---------+---------------------+-----------------------+

Setting the cache policy
~~~~~~~~~~~~~~~~~~~~~~~~

The cache policy can be set on the ``DataAPI`` object directly or in a configuration file.

Setting the cache policy through the Python API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Set the :py:attr:`~datafs.DataAPI.cache_policy` attribute on a :py:class:`~datafs.DataAPI` object:

.. example code

Setting the cache policy in a configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. example code


