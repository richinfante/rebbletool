__author__ = 'richinfante'

import os
import requests
import subprocess

from .base import BaseCommand
from ..sdk.manager import SDKManager

REPO_RELEASE_API = 'https://api.github.com/repos/richinfante/rebbletool/tags'
RELEASE_UI_BASE = 'https://github.com/richinfante/rebbletool/releases/tag/{tag}'

class UpdateCommand(BaseCommand):
    """Performs a self-update, assuming that the user cloned the repo as per the instructions"""
    command = 'update'

    def do_update(self):
        tool_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        # Pull the latest changes
        out = subprocess.check_output(['git', 'pull'], cwd=tool_dir).decode('ascii').strip()
        for line in out.split('\n'):
            print('git: %s' % line)

        # Install the latest SDK
        print('running `rebble sdk install latest`')
        sdkman = SDKManager()
        sdkman.install_remote_sdk('latest', force_reinstall=True)

    @staticmethod
    def get_tool_git_revision_hash() -> str:
        tool_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=tool_dir).decode('ascii').strip()

    @classmethod
    def add_parser(cls, parser):
        parser = super(UpdateCommand, cls).add_parser(parser)
        parser.add_argument('--force', action='store_true', help="Send the processes SIGKILL")
        return parser

    def __call__(self, args):
        super(UpdateCommand, self).__call__(args)
        current_release_hash = UpdateCommand.get_tool_git_revision_hash()

        releases = requests.get(REPO_RELEASE_API).json()
        sorted_releases = sorted(releases, key=lambda x: x['name'], reverse=True)

        current_release = [x for x in sorted_releases if x.get('commit') and x['commit']['sha'] == current_release_hash]

        if current_release:
            current_release_tag = current_release[0]['name']
        else:
            current_release_tag = None

        latest_release_hash = sorted_releases[0]['commit']['sha']
        latest_release_tag = sorted_releases[0]['name']

        if current_release_tag:
            print('current release: %s (%s) %s' % (current_release_tag, current_release_hash, RELEASE_UI_BASE.format(tag=current_release_tag)))
        else:
            print('current release: unknown (%s)' % current_release_hash)

        if current_release_hash != latest_release_hash:
            print('latest release: %s (%s) %s' % (latest_release_tag, latest_release_hash, RELEASE_UI_BASE.format(tag=latest_release_tag)))

        if current_release_hash != latest_release_hash:
            print('A new release is available, updating...')
            self.do_update()
        elif args.force:
            print('You are on the latest, but forcing update...')
            self.do_update()
        else:
            print('You are on the latest release. To force an update, use --force')
