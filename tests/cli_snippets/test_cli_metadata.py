
import pytest
import os
import ast


@pytest.mark.cli_snippets
def test_cli_snippets(cli_validator):

    # Snippet 1

    cli_validator('''

Snippet 1 setup

.. code-block:: bash

    $ datafs create my_archive

.. EXAMPLE-BLOCK-1-START

.. code-block:: bash

    $ datafs my_archive metadata
    {u'acta non verba': u'deeds not words', 
     u'actiones secundum fidei': u'action follows belief',
     u'ad undas': u'to the waves',
     u'as victoriam': u'for victory'}

.. EXAMPLE-BLOCK-1-END

''', interpreter=ast.literal_eval)

    # Snippet 2

    cli_validator('''

.. EXAMPLE-BLOCK-2-START

.. code-block:: bash

    $ datafs update_metadata my_archive 'acta non verba' 'Action is better than words' 'ad atrumque paratas' 'prepared for either alternative'

.. EXAMPLE-BLOCK-2-END

''')

    # Snippet 3

    cli_validator('''

.. EXAMPLE-BLOCK-3-START

.. code-block:: bash

    $ datafs metadata my_archive

    {u'acta non verba': u'Action is better than words', 
     u'actiones secundum fidei': u'action follows belief',
     u'ad undas': u'to the waves',
     u'as victoriam': u'for victory', 
     u'ad atrumque paratas': u'prepared for either alternative'}

.. EXAMPLE-BLOCK-3-END

Teardown

.. code-block:: bash

    $ datafs delete my_archive

''')
