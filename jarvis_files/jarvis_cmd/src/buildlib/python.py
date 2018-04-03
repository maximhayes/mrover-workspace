import os
import subprocess

from jarvis.core import shell, cd, quiet, ensure_dir

from . import Builder, BuildError


def run_pytest(wksp, command):
    try:
        wksp.product_exec(*command)
    except subprocess.CalledProcessError as e:
        if e.returncode != 5:
            return False
    return True


def generate_setup_py(wksp, intermediate, name, params):
    executable = params.get('executable', False) == 'True'
    wksp.template(
        'setup.py',
        os.path.join(intermediate, 'setup.py'),
        component=name,
        executable=executable)


class PythonBuilder(Builder):
    def is_relevant_file(self, name):
        return os.path.splitext(name)[1] == '.py'

    def _mkdirs(self, intermediate):
        ensure_dir(os.path.join(intermediate, 'src', self.name))

    def _destination_file_path(self, relpath):
        src_file = os.path.commonpath((relpath, 'src')) == 'src'
        if not src_file:
            return relpath
        else:
            parent = relpath
            paths = []
            while parent != 'src':
                parent, name = os.path.split(parent)
                paths.append(name)
            return os.path.join('src', self.name, *paths)

    def _build(self, intermediate):
        shell('touch src/{}/__init__.py'.format(self.name))
        generate_setup_py(self.wksp, intermediate, self.name, self.params)
        shell('flake8')
        with cd('src'):
            if not (run_pytest(
                    self.wksp, ('pytest', '--doctest-modules'))):
                raise BuildError("doctests failed")

        if not run_pytest(self.wksp, ('pytest',)):
            raise BuildError("unit tests failed")

        with quiet():
            self.wksp.product_exec('python', 'setup.py', 'develop')
