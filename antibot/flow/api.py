import logging
from os.path import join
from typing import List

import requests
from pynject import pynject
from requests import HTTPError

from antibot.addons.tokens import TokenProvider
from antibot.constants import API_ENDPOINT
from antibot.domain.api import HipchatAuth
from antibot.domain.configuration import Configuration
from antibot.domain.room import Room
from antibot.domain.user import User
from antibot.xmpp.utils import JID

DEFAULT_PARAMS = {'max-results': 1000, 'expand': 'items'}


@pynject
class HipchatApi:
    def __init__(self, configuration: Configuration, token_provider: TokenProvider):
        self.jid = JID(configuration.jid)
        self.auth = HipchatAuth(configuration.api_token)
        self.token_provider = token_provider

    def list_users(self) -> List[User]:
        for item in requests.get(join(API_ENDPOINT, 'user'), params=DEFAULT_PARAMS, auth=self.auth).json()['items']:
            yield User(item['xmpp_jid'], item['id'], item['name'], item['mention_name'], item['title'])

    def list_rooms(self) -> List[Room]:
        for item in requests.get(join(API_ENDPOINT, 'room'), params=DEFAULT_PARAMS, auth=self.auth).json()['items']:
            yield Room(item['xmpp_jid'], item['id'], item['name'])

    def get_users_id_in_room(self, room: Room):
        params = DEFAULT_PARAMS.copy()
        params['include-offline'] = 'true'
        for item in requests.get(join(API_ENDPOINT, 'room/{}/participant'.format(room.api_id)), params=params,
                                 auth=self.auth).json()['items']:
            print(item)
            yield item['id']

    def send_html_message(self, room: Room, message: str):
        data = {
            'message_format': 'html',
            'message': message,
        }
        if room.is_private:
            token = HipchatAuth(self.token_provider.get_token(room.addon, room))
        else:
            token = self.auth
        r = requests.post(join(API_ENDPOINT, 'room/{}/notification'.format(room.api_id)), json=data, auth=token)
        try:
            r.raise_for_status()
        except HTTPError:
            logging.getLogger(__name__).error(r.text)

    def send_text_message(self, room: Room, message: str):
        data = {
            'message_format': 'text',
            'message': message,
        }
        if room.is_private:
            token = HipchatAuth(self.token_provider.get_token(room.addon, room))
        else:
            token = self.auth
        r = requests.post(join(API_ENDPOINT, 'room/{}/notification'.format(room.api_id)), json=data, auth=token)
        try:
            r.raise_for_status()
        except HTTPError:
            logging.getLogger(__name__).error(r.text)
