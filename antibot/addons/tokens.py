from datetime import datetime, timedelta
from os.path import join

import requests
from pyckson import serialize, parse
from pymongo.database import Database

from antibot.domain.auth import AddOnInstallation
from antibot.addons.descriptors import AddOnDescriptor
from antibot.constants import ADDON_TOKENS_DB, ADDON_INSTALLATIONS_DB, ADDON_CAPABILITIES_DB, API_ENDPOINT
from antibot.domain.room import Room
from antibot.storage import Storage
from pynject import pynject


class TokenInformation:
    def __init__(self, access_token: str, expires_at: datetime, group_id: str, group_name: str, scope: str,
                 token_type: str):
        self.access_token = access_token
        self.expires_at = expires_at
        self.group_id = group_id
        self.group_name = group_name
        self.scope = scope
        self.token_type = token_type


@pynject
class TokenProvider:
    def __init__(self, db: Database):
        self.token_storage = Storage(ADDON_TOKENS_DB, db)
        self.auth_storage = Storage(ADDON_INSTALLATIONS_DB, db)
        self.capabilities_storage = Storage(ADDON_CAPABILITIES_DB, db)

    def refresh_token(self, addon: AddOnDescriptor, installation: AddOnInstallation) -> TokenInformation:
        token_data = requests.post(join(API_ENDPOINT, 'oauth/token'),
                                   auth=(installation.oauth_id, installation.oauth_secret),
                                   data={'grant_type': 'client_credentials',
                                         'scope': 'send_notification'}).json()

        expiration = datetime.now() + timedelta(seconds=token_data['expires_in'])
        token_info = TokenInformation(token_data['access_token'], expiration, token_data['group_id'],
                                      token_data['group_name'], token_data['scope'], token_data['token_type'])
        self.token_storage.save(addon.db_key(installation.room_id), serialize(token_info))
        return token_info

    def get_token(self, addon: AddOnDescriptor, room: Room):
        token_info = parse(TokenInformation, self.token_storage.get(addon.db_key(room.api_id)))
        if token_info.expires_at < datetime.now():
            addon_install = parse(AddOnInstallation, self.auth_storage.get(addon.db_key(room.api_id)))
            return self.refresh_token(addon, addon_install)
        return token_info
