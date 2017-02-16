import pytest


@pytest.mark.pattern
def test_required_archive_patterns(api_with_pattern):

    assert api_with_pattern.manager.required_archive_patterns == \
	                        ['string1', 'string2', 'string3', 'string4']
	api_with_pattern.create('string1/string2/string3',
		                     metadata=dict(description='some description'))

	