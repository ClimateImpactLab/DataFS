from datafs.datafs import cli
import shlex
import re


def get_command(string):
    '''
    Parses command into the command line arguments and expected stdin/stderr
    '''

    parsed = re.search(
        r'\ *\$ (?P<cmd>datafs[^\n]+)(?P<response>(\n\ +[^\n]+)*)',
        string)

    command = shlex.split(parsed.group('cmd'))[1:]
    response = '\n'.join(map(
        lambda s: s.strip(),
        parsed.group('response').strip().split('\n')))

    lines = response.split('\n')
    if lines[0] == 'Traceback (most recent call last):':
        response = None
        exception = ' '.join(map(lambda s: s.strip(), lines[2:]))
    else:
        exception = None

    return command, response, exception


def validate_command(config, command, error=False):
    '''
    Checks the result of running command against expected output
    '''

    runner, api, config_file, prefix = config

    command, response, exception = get_command(command)

    result = runner.invoke(cli, prefix + command)

    if error:
        assert result.exit_code != 0
        fmt = result.exc_info[0].__name__ + ': ' + str(result.exc_info[1])
        assert exception == fmt
    else:
        assert result.exit_code == 0
        assert result.output.strip() == response
