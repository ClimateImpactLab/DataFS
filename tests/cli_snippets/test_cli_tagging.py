
from __future__ import absolute_import

import pytest
from examples.snippets import cli_tagging


@pytest.mark.examples
@pytest.mark.cli_snippets
def test_cli_metadata_snippets(cli_validator):

    # Snippet 1

    cli_validator(cli_tagging.__doc__)
