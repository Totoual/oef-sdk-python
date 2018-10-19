# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Tom Nicholson <tom.nicholson@fetch.ai>
import distutils.cmd
import distutils.log
import fileinput
import os
import re
import shutil
import subprocess
import glob

import setuptools.command.build_py
from setuptools import setup

#TODO support installation for Windows

class ProtocCommand(distutils.cmd.Command):
    """A custom command to generate Python Protobuf modules from OEFCoreProtocol"""

    description = "Generate Python Protobuf modules from OEFCoreProtocol specifications."
    user_options = [
        # TODO: put the options like --proto_path and --python_out here
    ]

    def run(self):
        command = self._build_command()
        self._run_command(command)
        self._fix_import_statements_in_all_protobuf_modules()

    def _run_command(self, command):
        self.announce(
            "Running %s" % str(command),
            level=distutils.log.INFO
        )
        subprocess.check_call(command)

    def initialize_options(self):
        """Set default values for options."""
        # Each user option must be listed here with their default value.
        # TODO: complete
        pass

    def finalize_options(self):
        """Post-process options."""
        # TODO complete
        pass

    def _find_protoc_executable_path(self):
        # TODO: fix (and test) how to find protoc executable for other OS
        # the next line works in Python 3 but not in Python 2.
        # result = shutil.which("protoc")

        # Works also in Python 2
        result = os.popen("which protoc").read().strip()

        if result is None or result == "":
            raise EnvironmentError("protoc compiler not found.")
        return result

    def _build_command(self):
        protoc_executable_path = self._find_protoc_executable_path()
        command = [protoc_executable_path] + self._get_arguments()
        return command

    # TODO: generalize to other system path pattern (e.g. Windows' one)
    def _get_arguments(self):
        arguments = []
        arguments.append("--proto_path=./OEFCoreProtocol")
        arguments.append("--python_out=./oef_python")
        arguments += glob.glob("OEFCoreProtocol/*.proto") # TODO add recursive search
        return arguments

    def _fix_import_statements_in_all_protobuf_modules(self):
        # TODO: generalize to other system path pattern (e.g. Windows' one)
        generated_protobuf_python_modules = glob.glob("oef_python/*_pb2.py")
        for filepath in generated_protobuf_python_modules:
            self._fix_import_statements_in_protobuf_module(filepath)

    def _fix_import_statements_in_protobuf_module(self, filename):
        for line in fileinput.input(filename, inplace=True):
            line = re.sub("^(import \w*_pb2)", "from . \g<1>", line.strip())
            # stdout redirected to the file (fileinput.input with inplace=True)
            print(line)


class BuildPyCommand(setuptools.command.build_py.build_py):
    """Custom build command."""

    def run(self):
        self.run_command("protoc")
        setuptools.command.build_py.build_py.run(self)


setup(
    name='oef_python',
    version='0.1',
    packages=['oef_python'],
    cmdclass={
        'protoc': ProtocCommand,
        'build_py': BuildPyCommand
    }
)
