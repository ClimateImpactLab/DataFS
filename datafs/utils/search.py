import os
import click
import re

import whoosh.fields as fields
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser, FuzzyTermPlugin


def prep_index(indexdir, api=None, profile=None, config_file=None):
    '''
    Create an index populated by archive names
    '''

    schema=fields.Schema(
        title=fields.TEXT(stored=True),
        content=fields.TEXT)

    ix = create_in(indexdir, schema)

    writer = ix.writer()

    if api is None:
        api = get_api(profile=profile, config_file=config_file)

    for archive in api.list():
        writer.add_document(
            title=unicode(archive),
            content=unicode(' '.join(
                os.path.splitext(archive)[0].split('_') +
                re.split(r'[\-_]', os.path.splitext(archive)[0]) +
                [os.path.splitext(archive)[1][1:]])))

    writer.commit()


def get_index(indexdir, api=None, profile=None, config_file=None):
    '''
    Retrieve or create index in indexdir
    '''

    if indexdir is None:
        indexdir = os.path.join(click.get_app_dir('datafs'), 'index')

    if not os.path.isdir(indexdir):
        os.makedirs(indexdir)
    
    prep_index(indexdir, api=api, profile=profile, config_file=config_file)

    return open_dir(indexdir)


def query_index(schema, query):
    '''
    Parse a query using a schema with Fuzzy Term matching
    '''

    parser = QueryParser("content", schema)
    parser.add_plugin(FuzzyTermPlugin())
    return parser.parse(query)


def parse_next_chr(curstr, selection):
    '''
    Get next character from user and update search terms and selection
    '''

    last = click.getchar()

    if len(last) == 0:
        raise StopIteration

    elif len(last) > 1:
        # *nix-style arrow keys

        if list(map(ord, last)) == [27, 91, 65]:
            # *nix arrow up
            selection = max(selection-1, 0)

        elif list(map(ord, last)) == [27, 91, 66]:
            # *nix arrow down
            selection = min(selection + 1, 9)

    elif ord(last) == 945:
        # windows-style arrow keys

        direction = click.getchar()

        if ord(direction) == 72:
            # windows arrow up
            selection = max(selection-1, 0)

        elif ord(direction) == 80:
            # windows arrow down
            selection = min(selection + 1, 9)

    elif ord(last) in [8,127] and len(curstr) > 0:
        curstr = curstr[:-1]

    elif ord(last) in [13,24,25,27]:
        raise StopIteration

    else:
        curstr = curstr + last

    return curstr, selection


def search(query, indexdir=None, api=None, profile=None, config_file=None, limit=10):
    '''
    Search the index with query
    '''
    
    ix = get_index(indexdir, api=api, profile=profile, config_file=config_file)

    with ix.searcher() as searcher:

        parsed = query_index(ix.schema, query)
        
        results = searcher.search(parsed, limit=limit)

        return [r['title'] for r in results]


def interactive_search(indexdir=None, api=None, profile=None, config_file=None, limit=10):
    '''
    Start an interactive search session
    '''
    
    ix = get_index(indexdir, api=api, profile=profile, config_file=config_file)

    with ix.searcher() as searcher:

        curstr = ''
        prompt = 'Enter your search query (arrows to choose, enter to select): '
        selection = 0
        results = []

        click.clear()
        click.echo(prompt)

        while True:

            try:
                curstr, selection = parse_next_chr(curstr, selection)
            
            except StopIteration:
                break

            query_string = curstr+('*' if len(curstr) > 0 and curstr[-1] != ' ' else '')
            parsed = query_index(ix.schema, query_string)
            
            results = searcher.search(parsed, limit=limit)

            selection = min(selection, len(results)-1)

            click.clear()
            click.echo(prompt + curstr)
            for i, res in enumerate(results):
                click.echo(click.style(res['title'], bold = (i == selection)))

        click.clear()

        if len(results) > 0:
            return results[min(selection, len(results)-1)]['title']
