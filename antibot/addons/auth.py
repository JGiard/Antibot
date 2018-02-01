import logging
from typing import Union

import jwt
from bottle import request
from jwt import InvalidTokenError
from pyckson import parse
from pymongo.database import Database
from pynject import pynject

from antibot.addons.descriptors import AddOnDescriptor
from antibot.constants import ADDON_INSTALLATIONS_DB
from antibot.domain.auth import AddOnInstallation, AuthResult
from antibot.domain.room import Room
from antibot.repository.rooms import RoomsRepository
from antibot.repository.users import UsersRepository
from antibot.storage import Storage


@pynject
class AuthChecker:
    def __init__(self, db: Database, users_repo: UsersRepository, rooms_repo: RoomsRepository):
        self.rooms_repo = rooms_repo
        self.users_repo = users_repo
        self.storage = Storage(ADDON_INSTALLATIONS_DB, db)

    def check_auth(self, addon: AddOnDescriptor) -> Union[bool, AuthResult]:
        jwt_str = self.get_jwt_token()
        if not jwt_str:
            return False

        try:
            jwt_data = jwt.decode(jwt_str, verify=False)
        except InvalidTokenError:
            return False

        room_id = jwt_data['context']['room_id']
        data = self.storage.get(addon.db_key(room_id))
        if data is None:
            logging.error('could not find auth data for {}'.format(addon.db_key(room_id)))
            return False

        installation = parse(AddOnInstallation, data)

        try:
            jwt.decode(jwt_str, key=installation.oauth_secret)
            user = self.users_repo.by_id(int(jwt_data['sub']))
            room = self.rooms_repo.by_id(int(jwt_data['context']['room_id']))
            if room is None:
                room = Room('', jwt_data['context']['room_id'], 'Private', True, addon)
            return AuthResult(user, room)
        except InvalidTokenError:
            return False

    def get_jwt_token(self):
        if 'signed_request' in request.query:
            return request.query.signed_request
        if 'Authorization' in request.headers:
            auth = request.headers.get('Authorization')
            if auth[:3] == 'JWT':
                return auth[3:].strip()
