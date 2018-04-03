import os
import click
import configparser

import toposort

import buildlib
import buildlib.python
import buildlib.lcm
import buildlib.javascript
from buildlib import BuildError


def read_project_cfg(workspace, project):
    project_path = os.path.join(workspace.root, project)
    if not (os.path.isdir(project_path) and os.path.exists(
            os.path.join(project_path, 'project.ini'))):
        raise BuildError("project '{}' does not exist".format(project))

    project_cfg_path = os.path.join(project_path, 'project.ini')
    project_cfg = configparser.ConfigParser()
    project_cfg['build'] = {}
    project_cfg.read(project_cfg_path)
    return project_cfg


def get_deps(project_cfg):
    build_defs = project_cfg['build']
    deps = [s.strip().rstrip()
            for s in build_defs.get('deps', '').split(',')]
    if len(deps) == 1 and deps[0] == '':
        deps.pop()
    return deps


def gather_dependencies(workspace, project, project_cfg):
    deps = get_deps(project_cfg)
    all_deps = {
        project: set(deps)
    }

    for dep in deps:
        all_deps.update(gather_dependencies(
            workspace, dep, read_project_cfg(workspace, dep)))

    return all_deps


def build_project(workspace, project, config_args=[]):
    project_path = os.path.join(workspace.root, project)
    project_name = os.path.normpath(project).replace('/', '_')
    project_cfg = read_project_cfg(workspace, project)
    build_defs = project_cfg['build']
    deps = get_deps(project_cfg)
    build_defs.pop('deps', None)
    lang = build_defs.pop('lang', None)
    if lang is None:
        raise BuildError(
            "project '{}' does not have a specified language".format(
                project))

    # TODO Jarvis 2.3 will use build.py instead of project.ini
    builder_constructor = None
    if lang == 'python':
        builder_constructor = buildlib.python.PythonBuilder
    elif lang == 'lcm':
        builder_constructor = buildlib.lcm.LcmBuilder
    elif lang == 'js':
        builder_constructor = buildlib.javascript.YarnBuilder

    if builder_constructor is None:
        raise BuildError("unrecognized language '{}'".format(lang))
    builder = builder_constructor(workspace, project_path, project_name, deps,
                                  **build_defs)
    click.secho('Building {}...'.format(project), bold=True)
    builder.configure(config_args)
    builder.build()
    click.secho('Finished building {}'.format(project), fg='green')


def build(workspace, project, config_args=[]):
    project_cfg = read_project_cfg(workspace, project)

    dep_graph = gather_dependencies(workspace, project, project_cfg)
    try:
        dep_list = toposort.toposort_flatten(dep_graph)
    except toposort.CircularDependencyError:
        raise BuildError('circular dependencies detected!')

    for dep in dep_list:
        build_project(workspace, dep, config_args)
