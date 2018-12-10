# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
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


class ProtocCommand(distutils.cmd.Command):
    """A custom command to generate Python Protobuf modules from OEFCoreProtocol"""

    description = "Generate Python Protobuf modules from protobuf files specifications."
    user_options = [
        ("--proto_path", None, "Path to OEFCoreProtocol folder..")
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
        self.proto_path = "OEFCoreProtocol"

    def finalize_options(self):
        """Post-process options."""
        assert os.path.exists(self.proto_path), (
                'Directory %s does not exist.' % self.proto_path)

    def _find_protoc_executable_path(self):
        result = shutil.which("protoc")

        if result is None or result == "":
            raise EnvironmentError("protoc compiler not found.")
        return result

    def _build_command(self):
        protoc_executable_path = self._find_protoc_executable_path()
        command = [protoc_executable_path] + self._get_arguments()
        return command

    def _get_arguments(self):
        arguments = []
        arguments.append("--proto_path=%s" % self.proto_path)
        arguments.append("--python_out=oef")
        arguments += glob.glob(os.path.join("OEFCoreProtocol", "*.proto"))
        return arguments

    def _fix_import_statements_in_all_protobuf_modules(self):
        generated_protobuf_python_modules = glob.glob(os.path.join("oef", "*_pb2.py"))
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
    name='oef',
    version='0.1',
    packages=['oef'],
    cmdclass={
        'protoc': ProtocCommand,
        'build_py': BuildPyCommand
    },
    install_requires=["protobuf"]
)
