import os
import configparser

import buildlib
from buildlib import BuildError


def gather_dependencies(workspace, project):
    project_path = os.path.join(workspace.root, project)
    if not (os.path.isdir(project_path) and os.path.exists(
            os.path.join(project_path, 'project.ini'))):
        raise BuildError("project '{}' does not exist".format(project))

    project_cfg_path = os.path.join(project_path, 'project.ini')
    project_cfg = configparser.ConfigParser()
    project_cfg['build'] = {}
    project_cfg.read(project_cfg_path)

    build_defs = project_cfg['build']
    deps = [s.strip().rstrip()
            for s in build_defs.get('deps', '').split(',')]
    if len(deps) == 1 and deps[0] == '':
        deps.pop()

    all_deps = {
        project: deps
    }

    for dep in deps:
        all_deps.extend(gather_dependencies(workspace, dep))

    return all_deps


def build(workspace, project):
    project_path = os.path.join(workspace.root, project)
    if not (os.path.isdir(project_path) and os.path.exists(
            os.path.join(project_path, 'project.ini'))):
        raise BuildError("project '{}' does not exist".format(project))
    project_name = os.path.normpath(project).replace('/', '_')

    project_cfg_path = os.path.join(project_path, 'project.ini')
    project_cfg = configparser.ConfigParser()
    project_cfg['build'] = {}
    project_cfg.read(project_cfg_path)

    build_defs = project_cfg['build']
    deps = [s.strip().rstrip()
            for s in build_defs.get('deps', '').split(',')]
    if len(deps) == 1 and deps[0] == '':
        deps.pop()

    # TODO recursively build `deps`

    lang = build_defs.pop('lang', None)
    if lang is None:
        raise BuildError(
            "project '{}' does not have a specified language".format(
                project))

    # TODO Jarvis 2.2 will use build.py instead of project.ini
    builder_constructor = buildlib.Builder
    if lang == 'python':
        builder_constructor = buildlib.python.PythonBuilder
    builder = builder_constructor(workspace, project_path, project_name,
                                  **build_defs)
    builder.build()
