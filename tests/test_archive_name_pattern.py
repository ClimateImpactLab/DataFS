import pytest


@pytest.mark.pattern
def test_required_archive_patterns(api_with_pattern):

    assert api_with_pattern.manager.required_archive_patterns == [
            r'^(TLD1/(sub1|sub2|sub3)|TLD2/(sub1|sub2|sub3))']

    archive = api_with_pattern.create(
        'TLD1/sub1/substring1/substring1a.csv',
        metadata=dict(description='some description'))

    assert archive.archive_name == 'TLD1/sub1/substring1/substring1a.csv'

    archive2 = api_with_pattern.create(
        'TLD2/sub2/substring1/substring1a.csv',
        metadata=dict(description='some description'))

    assert archive2.archive_name == 'TLD2/sub2/substring1/substring1a.csv'

    archive3 = api_with_pattern.create(
        'TLD2/sub3/substring1/substring1a.csv',
        metadata=dict(description='some description'))

    assert archive3.archive_name == 'TLD2/sub3/substring1/substring1a.csv'

    with pytest.raises(ValueError):
        api_with_pattern.create(
            'SOME/string1/string2/string3.csv',
            metadata=dict(description='some description'))

    with pytest.raises(ValueError):
        api_with_pattern.create(
            'TLD1_sub1_substring1.txt',
            metadata=dict(description='some description'))
