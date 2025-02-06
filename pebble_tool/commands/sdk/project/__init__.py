from __future__ import absolute_import, print_function
__author__ = 'katharine'

import sys
import os
import subprocess
import logging

from pebble_tool.exceptions import (PebbleProjectException, InvalidJSONException, InvalidProjectException,
                                    OutdatedProjectException)
from pebble_tool.sdk.project import PebbleProject
from pebble_tool.util.analytics import post_event
from pebble_tool.commands.sdk import SDKCommand

logger = logging.getLogger("pebble_tool.commands.sdk")


class SDKProjectCommand(SDKCommand):
    @property
    def waf_path(self):
        return os.path.join(self.get_sdk_path(), 'pebble', 'waf')

    def _waf(self, command, extra_env=None, args=None):
        if args is None:
            args = []
        else:
            args = list(args)
        if self._verbosity > 0:
            v = '-' + ('v' * self._verbosity)
            args = [v] + args
        virtualenv = os.path.join(self.get_sdk_path(), '..', '.env')
        node_modules = os.path.join(self.get_sdk_path(), '..', 'node_modules')
        command = [os.path.join(virtualenv, 'bin', 'python'), self.waf_path, command] + args
        logger.debug("waf command: %s", subprocess.list2cmdline(command))
        env = os.environ.copy()
        env['PYTHONHOME'] = os.path.abspath(virtualenv)
        env['VIRTUAL_ENV'] = os.path.abspath(virtualenv)

        # add a few other paths to our bins, so the waf script can find them
        env['PATH'] = ':'.join([
            os.path.abspath(os.path.join(virtualenv, 'bin')),
            os.path.abspath(os.path.join(__file__, '../../../../../bin')),  # our bin with pebble bin, etc
            os.path.abspath(os.path.join(__file__, '../../../../../arm-cs-tools/bin')),  # build tools
            env['PATH']
        ])
        env['PYTHONPATH'] = ':'.join(sys.path)
        env['NODE_PATH'] = node_modules
        env['NOCLIMB'] = "1"  # This prevents waf from climbing into parent directories and executing commands

        if extra_env is not None:
            env.update(extra_env)

        logger.debug("env: ", env)
        logger.debug("run: %s" % subprocess.list2cmdline(command))

        subprocess.check_call(command, env=env)

    def __call__(self, args):
        super(SDKProjectCommand, self).__call__(args)
        try:
            self.project = PebbleProject()
        except PebbleProjectException as e:
            event_map = {
                InvalidProjectException: "sdk_run_without_project",
                InvalidJSONException: "sdk_json_error",
                OutdatedProjectException: "sdk_json_error",
            }
            if type(e) in event_map:
                post_event(event_map[type(e)])
            raise
