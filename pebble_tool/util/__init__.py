__author__ = 'katharine'

import os.path
import platform


def get_persist_dir():
    directory = os.path.abspath(os.path.join(__file__, '../../../sdk'))
    # print(directory)
    # exit(0)
    # if platform.system() == 'Darwin':
    #     dir = os.path.expanduser("~/Library/Application Support/Pebble SDK")
    # else:
    #     dir = os.path.expanduser("~/.pebble-sdk")
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory
