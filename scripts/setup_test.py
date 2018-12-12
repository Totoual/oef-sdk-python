# -*- coding: utf-8 -*-

# Copyright 2018, Fetch AI Ltd. All Rights Reserved.

"""
Script that clone the OEFCore repository and build the OEFCore Node.
You must have the OEFCore built in order to run tests successfully.
"""
import os
import subprocess
import sys

from git import Repo, RemoteProgress, InvalidGitRepositoryError


def build_project(project_root, build_root, options):
    print('Source.:', project_root)
    print('Build..:', build_root)
    print('Options:')
    for key, value in options.items():
        print(' - {} = {}'.format(key, value))
    print('\n')

    # ensure the build directory exists
    os.makedirs(build_root, exist_ok=True)

    # run cmake
    cmd = ['cmake']
    cmd += [project_root]
    exit_code = subprocess.call(cmd, cwd=build_root)
    if exit_code != 0:
        print('Failed to configure cmake project')
        sys.exit(exit_code)

    # make the project
    if os.path.exists(os.path.join(build_root, "build.ninja")):
        cmd = ["ninja"]
    else:
        cmd = ['make', '-j']
    exit_code = subprocess.call(cmd, cwd=build_root)
    if exit_code != 0:
        print('Failed to make the project')
        sys.exit(exit_code)


def main():

    if not os.path.exists("oef-core"):
        # TODO change url
        Repo.clone_from("git@github.com:uvue-git/oef-core.git", "oef-core", progress=RemoteProgress())
    else:
        try:
            Repo("oef-core")
        except InvalidGitRepositoryError:
            print("Repository is not valid.")
            exit(1)

    build_project("..", "oef-core/build", {})


if __name__ == '__main__':
    main()
