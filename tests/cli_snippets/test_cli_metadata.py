
import pytest


@pytest.mark.examples
@pytest.mark.cli_snippets
def test_cli_metadata_snippets(cli_validator):

    # Snippet 1

    cli_validator(r'''

Snippet 1 setup

.. code-block:: bash

    $ datafs create my_archive \
    >     --description "my example archive" \
    >     --source "Burke et al. (2016)" \
    >     --doi '10.1038/nature15725' \
    >     --author "Burke"
    created versioned archive <DataArchive local://my_archive>

.. EXAMPLE-BLOCK-1-START

.. code-block:: bash

    $ datafs metadata my_archive # doctest: +SKIP
    {u'description': u'my example archive',
     u'source': u'Burke et al. (2016)',
     u'doi': u'10.1038/nature15725',
     u'author': u'fBurke'}

.. EXAMPLE-BLOCK-1-END


Snippet 2

.. EXAMPLE-BLOCK-2-START

.. code-block:: bash

    $ datafs update_metadata my_archive \
    >     --description 'Spatial impact meta-analysis' \
    >     --method 'downscaled Burke et al (2015) data'

.. EXAMPLE-BLOCK-2-END


Snippet 3

.. EXAMPLE-BLOCK-3-START

.. code-block:: bash

    $ datafs metadata my_archive # doctest: +SKIP
    {u'description': u'Spatial impact meta-analysis',
     u'source': u'Burke et al. (2016)',
     u'doi': u'10.1038/nature15725',
     u'author': u'Burke',
     u'method': u'downscaled Burke et al (2015) data'}

.. EXAMPLE-BLOCK-3-END

Teardown

.. code-block:: bash

    $ datafs delete my_archive
    deleted archive <DataArchive local://my_archive>

''')
