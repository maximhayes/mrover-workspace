import click
import os

import buildlib
from .core import cd, quiet, cp, shell


def install_deps(wksp):
    ensure_lcm(wksp)


def check_lcm(wksp):
    if not wksp.product_file_exists('bin', 'lcm-gen'):
        return False

    if not wksp.product_file_exists('lib', 'liblcm.so'):
        return False

    try:
        with quiet():
            wksp.product_exec(
                    'python', '-c', 'import lcm')
    except:
        return False

    return True


def ensure_lcm(wksp):
    if check_lcm(wksp):
        click.echo("LCM already installed, skipping.")
        return

    wksp.ensure_product_env()
    lcmdir = os.path.join(wksp.third_party_root, 'lcm')
    lcm_scratch = os.path.join(wksp.intermediate, 'lcm')
    cp(lcmdir, lcm_scratch)
    try:
        with cd(lcm_scratch):
            click.echo("Configuring LCM...")
            with quiet():
                shell('./bootstrap.sh')
                wksp.product_exec(
                        '/bin/sh',
                        './configure', '--prefix={}'.format(wksp.product_env))
            click.echo("Building LCM...")
            with quiet():
                wksp.product_exec('make')
            click.echo("Installing LCM...")
            with quiet():
                wksp.product_exec('make', 'install')
                with cd('lcm-python'):
                    wksp.product_exec('python', 'setup.py', 'install')
    except:
        raise buildlib.BuildError('failed to build LCM')

    click.echo("Finished installing LCM.")
