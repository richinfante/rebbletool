from __future__ import absolute_import

import httplib2
import json
import os
import os.path
import requests

from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import Credentials
from oauth2client.file import Storage
import oauth2client.tools as tools

from pebble_tool.util import get_persist_dir

AUTH_SERVER   = os.getenv("PEBBLE_OAUTH_SERVER", "https://auth.rebble.io")
AUTHORIZE_URI = AUTH_SERVER + "/oauth/authorize"
TOKEN_URI     = AUTH_SERVER + "/oauth/token"
ME_URI        = AUTH_SERVER + "/api/v1/me.json"

SDK_CLIENT_ID     = os.getenv("PEBBLE_OAUTH_APP_ID", "8b9140c7b1f101a84a26cab03e6b12273af36829d0e6540394dae61196fe5e7b")
SDK_CLIENT_SECRET = os.getenv("PEBBLE_OAUTH_APP_SECRET", "8fdcbceafcbca6f9fdb6432cfcc246180bb59bcea957795b12efb5527397e2a1")

flow = OAuth2WebServerFlow(
    client_id=SDK_CLIENT_ID,
    client_secret=SDK_CLIENT_SECRET,
    scope="public",
    auth_uri=AUTHORIZE_URI,
    token_uri=TOKEN_URI
)


class Account(object):
    def __init__(self, persistent_dir):
        self.persistent_dir = persistent_dir
        self.storage = Storage(os.path.join(self.persistent_dir, 'oauth_storage'))
        self._user_info = None
        self._get_user_info()

    @property
    def is_logged_in(self):
        return True if self.storage.get() else False

    def get_credentials(self):
        return self.storage.get()

    def refresh_credentials(self):
        creds = self.get_credentials()
        if creds:
            creds.refresh(httplib2.Http())

    def get_access_token(self):
        creds = self.get_credentials()
        token_info = creds.get_access_token()
        return token_info.access_token

    bearer_token = property(get_access_token)

    @property
    def id(self):
        return self._get_user_info()['id']

    @property
    def name(self):
        return self._get_user_info()['name']

    @property
    def email(self):
        return self._get_user_info()['email']

    @property
    def roles(self):
        return self._get_user_info()['roles']

    @property
    def legacy_id(self):
        return self._get_user_info()['legacy_id']

    @property
    def _user_info_path(self):
        return os.path.join(self.persistent_dir, 'user_info')

    # hack to fix null token expiration
    def _set_expiration_to_long_time(self, creds):
        cred_str = creds.to_json()
        cred_json = json.loads(cred_str)
        # in case it might have an expiration
        if(cred_json['token_expiry'] is not None):
            return creds
        cred_json['token_expiry'] = '2100-01-01T00:00:01Z'
        cred_new_json = json.dumps(cred_json)
        return Credentials.new_from_json(cred_new_json)

    def login(self, args):
        creds = self._set_expiration_to_long_time(tools.run_flow(flow, self.storage, args))

        self.storage.put(creds)
        self.user_info = self._get_user_info()

    def logout(self):
        self.storage.delete()
        os.unlink(self._user_info_path)

    def _get_user_info(self):
        if self._user_info is not None:
            return self._user_info

        if not self.is_logged_in:
            return None

        file_path = self._user_info_path
        try:
            with open(file_path) as f:
                return json.load(f)
        except (IOError, ValueError):
            with open(file_path, 'w') as f:
                result = requests.get(ME_URI, headers={'Authorization': 'Bearer %s' % self.get_access_token()})
                result.raise_for_status()
                account_info = result.json()
                stored_info = {
                    'id': account_info['id'],
                    'name': account_info['name'],
                    'email': account_info['email'],
                    'roles': account_info['roles'],
                    'legacy_id': account_info.get('legacy_id', None)
                }
                json.dump(stored_info, f)
                self._user_info = stored_info
                return self._user_info


def get_default_account():
    path = os.path.join(get_persist_dir(), 'oauth')
    if not os.path.exists(path):
        os.makedirs(path)
    return Account(path)
