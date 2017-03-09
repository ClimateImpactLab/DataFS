# -*- coding: utf-8 -*-


from __future__ import absolute_import

from datafs import __version__
from datafs.config.config_file import ConfigFile
from datafs.config.helpers import (
    get_api,
    _parse_requirement,
    _interactive_config)
from datafs._compat import u
import click
import sys
import pprint


def _parse_args_and_kwargs(passed_args):

    args = []
    kwargs = {}

    has_kwargs = False

    while len(passed_args) > 0:

        arg = passed_args.pop(0)

        if arg[:2] == '--':
            has_kwargs = True

            if not len(passed_args) > 0:
                raise ValueError('Argument "{}" not recognized'.format(arg))

            kwargs[arg[2:]] = passed_args.pop(0)

        else:
            if has_kwargs:
                raise ValueError(
                    'Positional argument "{}" after keyword arguments'.format(
                        arg))

            args.append(arg)

    return args, kwargs


def _interactive_configuration(api, config, profile=None):

    profile = config.default_profile if profile is None else profile

    profile_config = config.get_profile_config(profile)

    # read from the required config settings in DataAPI
    _interactive_config(
        to_populate=profile_config['api']['user_config'],
        prompts=api.manager.required_user_config)

    config.config['profiles'][profile] = profile_config


def _parse_dependencies(dependency_args):

    if len(dependency_args) == 0:
        return None

    # dependencies = {}
    return dict(map(_parse_requirement, dependency_args))


def _generate_api(ctx):

    ctx.obj.config.read_config()

    if ctx.obj.profile is None:
        ctx.obj.profile = ctx.obj.config.config['default-profile']

    ctx.obj.api = get_api(
        profile=ctx.obj.profile,
        config_file=ctx.obj.config_file,
        requirements=ctx.obj.requirements)


class _DataFSInterface(object):

    def __init__(self):
        pass

# this sets the command line environment for


@click.group(
    name='datafs',
    short_help='An abstraction layer for data storage systems')
@click.option(
    '--config-file',
    envvar='DATAFS_CONFIG_FILE',
    type=str,
    help='Specify a configuration file')
@click.option(
    '--requirements',
    envvar='DATAFS_REQUIREMENTS_FILE',
    type=str,
    default=None,
    help='Specify a requirements file')
@click.option(
    '--profile',
    envvar='DATAFS_DEFAULT_PROFILE',
    type=str,
    default=None,
    help='Specify a config profile')
@click.version_option(version=__version__, prog_name='datafs')
@click.pass_context
def cli(
        ctx,
        config_file=None,
        requirements=None,
        profile=None):
    '''
    An abstraction layer for data storage systems

    DataFS is a package manager for data. It manages file versions,
    dependencies, and metadata for individual use or large organizations.

    For more information, see the docs at https://datafs.readthedocs.io
    '''

    ctx.obj = _DataFSInterface()

    ctx.obj.config_file = config_file
    ctx.obj.config = ConfigFile(ctx.obj.config_file)

    ctx.obj.requirements = requirements
    ctx.obj.profile = profile

    def teardown():
        if hasattr(ctx.obj, 'api'):
            ctx.obj.api.close()

    ctx.call_on_close(teardown)


@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True))
@click.option('--helper', is_flag=True, help='Prompt for user metadata')
@click.option('--edit', is_flag=True, help='Edit the config file manually')
@click.pass_context
def configure(ctx, helper, edit):
    '''
    Update configuration
    '''

    if edit:
        ctx.obj.config.edit_config_file()
        return

    _generate_api(ctx)

    kwargs = {ctx.args[i][2:]: ctx.args[i + 1]
              for i in xrange(0, len(ctx.args), 2)}
    ctx.obj.config.config['profiles'][ctx.obj.profile][
        'api']['user_config'].update(kwargs)

    ctx.obj.api.user_config.update(kwargs)

    if helper:
        _interactive_configuration(
            ctx.obj.api,
            ctx.obj.config,
            profile=ctx.obj.profile)

    else:
        for kw in ctx.obj.api.manager.required_user_config:
            if kw not in ctx.obj.api.user_config:
                raise KeyError(
                    'Required configuration option "{}" not supplied. '
                    'Use --helper to configure interactively'.format(kw))

    ctx.obj.config.write_config(ctx.obj.config_file)


@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True),
    short_help='Create an archive')
@click.argument('archive_name')
@click.option('--authority_name', default=None)
@click.option('--versioned/--not-versioned', default=True)
@click.option('-t', '--tag', multiple=True)
@click.option('--helper', is_flag=True)
@click.pass_context
def create(
        ctx,
        archive_name,
        authority_name,
        versioned=True,
        tag=None,
        helper=False):
    '''
    Create an archive
    '''

    tags = list(tag)

    _generate_api(ctx)
    args, kwargs = _parse_args_and_kwargs(ctx.args)
    assert len(args) == 0, 'Unrecognized arguments: "{}"'.format(args)

    var = ctx.obj.api.create(
        archive_name,
        authority_name=authority_name,
        versioned=versioned,
        metadata=kwargs,
        tags=tags,
        helper=helper)

    verstring = 'versioned archive' if versioned else 'archive'
    click.echo('created {} {}'.format(verstring, var))


@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True),
    short_help='Update an archive with new contents')
@click.argument('archive_name')
@click.option('--bumpversion', default='patch')
@click.option('--prerelease', default=None)
@click.option('--dependency', multiple=True)
@click.option('-m', '--message', default=None)
@click.option('--string', is_flag=True)
@click.argument('file', default=None, required=False)
@click.pass_context
def update(
        ctx,
        archive_name,
        bumpversion='patch',
        prerelease=None,
        dependency=None,
        message=None,
        string=False,
        file=None):
    '''
    Update an archive with new contents
    '''

    _generate_api(ctx)

    args, kwargs = _parse_args_and_kwargs(ctx.args)
    assert len(args) == 0, 'Unrecognized arguments: "{}"'.format(args)

    dependencies_dict = _parse_dependencies(dependency)

    var = ctx.obj.api.get_archive(archive_name)
    latest_version = var.get_latest_version()

    if string:

        with var.open(
                'w+',
                bumpversion=bumpversion,
                prerelease=prerelease,
                dependencies=dependencies_dict,
                metadata=kwargs,
                message=message) as f:

            if file is None:
                for line in sys.stdin:
                    f.write(u(line))
            else:
                f.write(u(file))

    else:
        if file is None:
            file = click.prompt('enter filepath')

        var.update(
            file,
            bumpversion=bumpversion,
            prerelease=prerelease,
            dependencies=dependencies_dict,
            metadata=kwargs,
            message=message)

    new_version = var.get_latest_version()

    if latest_version is None and new_version is not None:
        bumpmsg = ' new version {} created.'.format(
            new_version)

    elif new_version != latest_version:
        bumpmsg = ' version bumped {} --> {}.'.format(
            latest_version, new_version)

    elif var.versioned:
        bumpmsg = ' version remains {}.'.format(latest_version)
    else:
        bumpmsg = ''

    click.echo('uploaded data to {}.{}'.format(var, bumpmsg))


@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True),
    short_help='Update an archive\'s metadata')
@click.argument('archive_name')
@click.pass_context
def update_metadata(ctx, archive_name):
    '''
    Update an archive's metadata
    '''

    _generate_api(ctx)
    args, kwargs = _parse_args_and_kwargs(ctx.args)
    assert len(args) == 0, 'Unrecognized arguments: "{}"'.format(args)

    var = ctx.obj.api.get_archive(archive_name)

    var.update_metadata(metadata=kwargs)


@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True),
    short_help='Set the dependencies of an archive')
@click.argument('archive_name')
@click.option('--dependency', multiple=True)
@click.pass_context
def set_dependencies(ctx, archive_name, dependency=None):
    '''
    Set the dependencies of an archive
    '''

    _generate_api(ctx)
    kwargs = _parse_dependencies(dependency)

    var = ctx.obj.api.get_archive(archive_name)

    var.set_dependencies(dependencies=kwargs)


@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True),
    short_help='List the dependencies of an archive')
@click.argument('archive_name')
@click.option('--version', default=None)
@click.pass_context
def get_dependencies(ctx, archive_name, version):
    '''
    List the dependencies of an archive
    '''

    _generate_api(ctx)

    var = ctx.obj.api.get_archive(archive_name)

    deps = []

    dependencies = var.get_dependencies(version=version)
    for arch, dep in dependencies.items():
        if dep is None:
            deps.append(arch)
        else:
            deps.append('{}=={}'.format(arch, dep))

    click.echo('\n'.join(deps))


@cli.command(short_help='Add tags to an archive')
@click.argument('archive_name')
@click.argument('tags', nargs=-1)
@click.pass_context
def add_tags(ctx, archive_name, tags):
    '''
    Add tags to an archive
    '''

    _generate_api(ctx)

    var = ctx.obj.api.get_archive(archive_name)

    var.add_tags(*tags)


@cli.command(short_help='Remove tags from an archive')
@click.argument('archive_name')
@click.argument('tags', nargs=-1)
@click.pass_context
def delete_tags(ctx, archive_name, tags):
    '''
    Remove tags from an archive
    '''

    _generate_api(ctx)

    var = ctx.obj.api.get_archive(archive_name)

    var.delete_tags(*tags)


@cli.command(short_help='Print tags assigned to an archive')
@click.argument('archive_name')
@click.pass_context
def get_tags(ctx, archive_name):
    '''
    Print tags assigned to an archive
    '''

    _generate_api(ctx)

    var = ctx.obj.api.get_archive(archive_name)

    click.echo(' '.join(var.get_tags()), nl=False)
    print('')


@cli.command(short_help='Download an archive')
@click.argument('archive_name')
@click.argument('filepath')
@click.option('--version', default=None)
@click.pass_context
def download(ctx, archive_name, filepath, version):
    '''
    Download an archive
    '''

    _generate_api(ctx)
    var = ctx.obj.api.get_archive(archive_name)

    if version is None:
        version = var.get_default_version()

    var.download(filepath, version=version)

    archstr = var.archive_name +\
        '' if (not var.versioned) else ' v{}'.format(version)

    click.echo('downloaded{} to {}'.format(archstr, filepath))


@cli.command(short_help='Echo the contents of an archive')
@click.argument('archive_name')
@click.option('--version', default=None)
@click.pass_context
def cat(ctx, archive_name, version):
    '''
    Echo the contents of an archive
    '''

    _generate_api(ctx)
    var = ctx.obj.api.get_archive(archive_name)

    with var.open('r', version=version) as f:
        for chunk in iter(lambda: f.read(1024 * 1024), ''):
            click.echo(chunk)


@cli.command(short_help='Get the version log for an archive')
@click.argument('archive_name')
@click.pass_context
def log(ctx, archive_name):
    '''
    Get the version log for an archive
    '''

    _generate_api(ctx)
    ctx.obj.api.get_archive(archive_name).log()


@cli.command(short_help='Get an archive\'s metadata')
@click.argument('archive_name')
@click.pass_context
def metadata(ctx, archive_name):
    '''
    Get an archive's metadata
    '''

    _generate_api(ctx)
    var = ctx.obj.api.get_archive(archive_name)
    click.echo(pprint.pformat(var.get_metadata()))


@cli.command(short_help='Get archive history')
@click.argument('archive_name')
@click.pass_context
def history(ctx, archive_name):
    '''
    Get archive history
    '''

    _generate_api(ctx)
    var = ctx.obj.api.get_archive(archive_name)
    click.echo(pprint.pformat(var.get_history()))


@cli.command(short_help='Get an archive\'s versions')
@click.argument('archive_name')
@click.pass_context
def versions(ctx, archive_name):
    '''
    Get an archive's versions
    '''

    _generate_api(ctx)

    var = ctx.obj.api.get_archive(archive_name)
    click.echo(pprint.pformat(map(str, var.get_versions())))


@click.command(short_help='List all archives matching filter criteria')
@click.option(
    '--prefix',
    default=None,
    help='filter archives based on initial character pattern')
@click.option(
    '--pattern',
    default=None,
    help='filter archive names with a match pattern')
@click.option(
    '--engine',
    default='path',
    help='comparison engine: str/path/regex (default path)')
@click.pass_context
def filter_archives(ctx, prefix, pattern, engine):
    '''
    List all archives matching filter criteria
    '''

    _generate_api(ctx)

    # want to achieve behavior like click.echo(' '.join(matches))

    for i, match in enumerate(ctx.obj.api.filter(
            pattern, engine, prefix=prefix)):

        click.echo(match, nl=False)
        print('')


cli.add_command(filter_archives, name='filter')


@cli.command(short_help='List all archives matching tag search criteria')
@click.argument('tags', nargs=-1)
@click.option(
    '--prefix',
    default=None,
    help='filter archives based on initial character pattern')
@click.pass_context
def search(ctx, tags, prefix=None):
    '''
    List all archives matching tag search criteria
    '''

    _generate_api(ctx)

    for i, match in enumerate(ctx.obj.api.search(*tags, prefix=prefix)):

        click.echo(match, nl=False)
        print('')


@cli.command(short_help='List archive path components at a given location')
@click.argument('location')
@click.option(
    '-a',
    '--authority_name',
    default=None,
    help='Name of the authority to search')
@click.pass_context
def listdir(ctx, location, authority_name=None):
    '''
    List archive path components at a given location

    Note:

    When using listdir on versioned archives, listdir will provide the
    version numbers when a full archive path is supplied as the location
    argument. This is because DataFS stores the archive path as a directory
    and the versions as the actual files when versioning is on.

    Parameters
    ----------

    location : str

        Path of the "directory" to search

        `location` can be a path relative to the authority root (e.g
        `/MyFiles/Data`) or can include authority as a protocol (e.g.
        `my_auth://MyFiles/Data`). If the authority is specified as a
        protocol, the `authority_name` argument is ignored.

    authority_name : str

        Name of the authority to search (optional)

        If no authority is specified, the default authority is used (if
        only one authority is attached or if
        :py:attr:`DefaultAuthorityName` is assigned).


    Returns
    -------

    list

        Archive path components that exist at the given "directory"
        location on the specified authority

    Raises
    ------

    ValueError

        A ValueError is raised if the authority is ambiguous or invalid
    '''

    _generate_api(ctx)

    for path_component in ctx.obj.api.listdir(
            location,
            authority_name=authority_name):

        click.echo(path_component, nl=False)
        print('')


@cli.command(short_help='Delete an archive')
@click.argument('archive_name')
@click.pass_context
def delete(ctx, archive_name):
    '''
    Delete an archive
    '''

    _generate_api(ctx)
    var = ctx.obj.api.get_archive(archive_name)

    var.delete()
    click.echo('deleted archive {}'.format(var))


if __name__ == '__main__':
    cli()
