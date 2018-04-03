import click
import subprocess
from click_didyoumean import DYMGroup
import os
import sys

import buildlib
from .core import Workspace
from . import building, third_party


def search_for_workspace_root(start):
    parent = start
    while parent != '/':
        jarvis_script = os.path.join(parent, 'jarvis')
        if os.path.exists(jarvis_script):
            # we've found the workspace root
            return parent
        parent = os.path.dirname(parent)
    return None


def search_for_executable(bindir, name):
    bins = os.scandir(bindir)
    for entry in bins:
        if (entry.is_file() and entry.name == name and
                os.access(entry.path, os.X_OK)):
            return entry.path

    if hasattr(bins, 'close'):
        bins.close()
    return None


pass_workspace = click.make_pass_decorator(Workspace)


@click.group(cls=DYMGroup)
@click.option('-w', '--workspace',
              envvar='JARVIS_WORKSPACE', default=None,
              type=click.Path(exists=True))
@click.pass_context
def cli(ctx, workspace):
    '''
    Jarvis 2.1 -- MRover build system
    '''
    if workspace is None:
        workspace = search_for_workspace_root(os.getcwd())

    if workspace is None:
        click.secho("error: can't find the workspace root", fg='red')
        sys.exit(1)

    ctx.obj = Workspace(workspace)


@cli.command()
@click.argument('project')
@pass_workspace
def build(workspace, project):
    '''
    build a project
    '''
    try:
        third_party.install_deps(workspace)
        building.build(workspace, project)
    except buildlib.BuildError as e:
        click.secho('error: {}'.format(str(e)), fg='red', bold=True)
        sys.exit(1)


@cli.command()
@pass_workspace
def clean(workspace):
    '''
    removes the product env, requiring a full rebuild
    '''
    workspace.clean()


@cli.command()
@pass_workspace
def dep(workspace):
    '''
    installs 3rdparty folder into product env
    '''
    try:
        third_party.install_deps(workspace)
        click.secho("Done installing third party deps", fg='green')
    except buildlib.BuildError as e:
        click.secho('error: {}'.format(str(e)), fg='red', bold=True)
        sys.exit(1)


@cli.command(short_help='runs a command')
@click.argument('command', nargs=-1)
@pass_workspace
def exec(workspace, command):
    '''
    runs a command

    The product env will be searched first, followed by the Jarvis env.
    '''
    try:
        if os.path.exists(workspace.product_env):
            executable = search_for_executable(os.path.join(
                workspace.product_env, 'bin'), command[0])
            if executable is not None:
                workspace.product_exec(*command)
                return

        executable = search_for_executable(os.path.join(
            workspace.jarvis_env, 'bin'), command[0])
        if executable is not None:
            workspace.jarvis_exec(*command)
            return
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

    click.secho('error: cannot exec {}'.format(command), fg='red')


@cli.command()
def implode():
    '''
    destroys the temporary environments
    '''
    pass
