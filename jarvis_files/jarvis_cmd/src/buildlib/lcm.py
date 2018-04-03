import os

from jarvis.core import mkdir, cd, cp, quiet
from . import Builder
from .python import generate_setup_py


class LcmBuilder(Builder):
    def is_relevant_file(self, f):
        return os.path.splitext(f)[1] == '.lcm'

    def _build(self, intermediate):
        mkdir('python')
        mkdir('cpp')

        lcm_files = [
            f.path
            for f in os.scandir(intermediate)
        ]
        self.wksp.product_exec(
                'lcm-gen', '--python', *lcm_files, '--ppath', 'python')
        generate_setup_py(
            self.wksp,
            os.path.join(intermediate, 'python'),
            'rover_msgs', {})
        with cd('python'):
            with quiet():
                self.wksp.product_exec(
                     'python', 'setup.py', 'develop')

        with cd('cpp'):
            self.wksp.product_exec(
                    'lcm-gen', '--cpp', *lcm_files, '--cpp-std=c++11')
            target = os.path.join(self.wksp.product_env,
                                  'include', 'rover_msgs')
            cp('rover_msgs', target)
