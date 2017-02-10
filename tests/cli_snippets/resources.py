from datafs.datafs import cli
import shlex
import re
import traceback


def get_command(string):
    r"""
    Parses command into the command line arguments and expected stdin/stderr

    Example
    -------

    .. code-block:: python

        >>> test = '''
        ... .. code-block:: bash
        ... 
        ...     $ echo "my string" 
        ...     ['echo', 'my string']
        ...
        ... '''
        >>> next(get_command(test))
        (['echo', 'my string'], "['echo', 'my string']", None)

    .. code-block:: python

        >>> test = '''
        ...
        ... .. code-block:: bash
        ... 
        ...     $ pytest test_nonexistant.py --cov=datafs --cov=examples \
        ...     >   --cov=docs --doctest-modules --cov-report term-missing
        ...     Traceback (most recent call last):
        ...     ...
        ...     ERROR: file not found: test_nonexistant.py
        ...
        ... '''
        >>> next(get_command(test))
        (['pytest', 'test_nonexistant.py', '--cov=datafs', '--cov=examples', '--cov=docs', '--doctest-modules', '--cov-report', 'term-missing'], None, 'ERROR: file not found: test_nonexistant.py')



    """

    for parsed in re.finditer(
            (r'(?P<cmd>\$\s+[^\n]+(\\\s*\n\s+\>\ +[^\n]+)*)'
            +r'(?P<res>(\n\ +[^\$\>\s][^\n]*)*)?'),
            string):

        cmd = parsed.group('cmd').split('\n')

        formatted = map(
            lambda s: re.sub(r'\s*[\$\>]\s*', ' ', s.strip()).strip(), cmd)

        command = shlex.split(' '.join(formatted))

        response = '\n'.join(map(
            lambda s: s.strip(),
            parsed.group('res').strip().split('\n')))

        lines = response.split('\n')
        if lines[0] == 'Traceback (most recent call last):':
            response = None
            exception = ' '.join(map(lambda s: s.strip(), lines[2:]))
        else:
            exception = None

        yield command, response, exception


def validate_command(config, command, error=False, interpreter=None):
    '''
    Checks the result of running command against expected output
    '''

    if interpreter is None:
        interpreter = lambda x: x

    runner, api, config_file, prefix = config

    for command, response, exception in get_command(command):

        if (len(command) == 0) or (command[0] != 'datafs'):
            continue

        result = runner.invoke(cli, prefix + command[1:])

        if error:
            assert result.exit_code != 0, result.output
            fmt = result.exc_info[0].__name__ + ': ' + str(result.exc_info[1])
            assert exception == fmt
        else:
            msg = '\n'+'\n'.join(traceback.format_exception(*result.exc_info))
            if result.exit_code != 0:
                raise ValueError("Errors encountered in execution: {}".format(msg))

            msg = '{0} != {1}\n\n+ {0}\n- {1}'.format(result.output, response)
            assert interpreter(result.output.strip()) == interpreter(response), msg

if __name__ == '__main__':
    import doctest
    doctest.testmod()