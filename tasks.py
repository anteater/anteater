# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
import os
import sys

from invoke import task, run

docs_dir = 'docs'
build_dir = os.path.join(docs_dir, '_build')


@task
def test(ctx):
    run('python setup.py test', pty=True)


@task
def clean(ctx):
    ctx.run("rm -rf build")
    ctx.run("rm -rf dist")
    ctx.run("rm -rf anteater.egg-info")
    clean_docs(ctx)
    print("Cleaned up.")


@task
def clean_docs(ctx):
    ctx.run("rm -rf %s" % build_dir)


@task
def browse_docs(ctx):
    ctx.run("open %s" % os.path.join(build_dir, 'index.html'))


@task
def build_docs(ctx, clean=False, browse=False):
    if clean:
        clean_docs()
    ctx.run("sphinx-build %s %s" % (docs_dir, build_dir), pty=True)
    if browse:
        browse_docs()


@task
def readme(ctx, browse=False):
    ctx.run('rst2html.py README.rst > README.html')


@task
def build(ctx):
    """Build source distribution and wheels."""
    ctx.run('python setup.py sdist bdist_wheel')


@task
def publish(ctx, test=False):
    """Publish to the cheeseshop.

    This command follows the Python packaging guidelines:
    https://packaging.python.org/tutorials/distributing-packages

    Information on configuration required for '--test' can be found
    here: https://wiki.python.org/moin/TestPyPI

    Before uploading please ensure you've signed the release using:

      gpg --detach-sign -a dist/package-1.0.1.tar.gz
    """
    if test:
        ctx.run('twine upload -r test dist/*')
    else:
        ctx.run("twine upload dist/*")
