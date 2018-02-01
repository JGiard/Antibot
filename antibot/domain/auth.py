from antibot.domain.room import Room
from antibot.domain.user import User


class AddOnInstallation:
    def __init__(self, capabilities_url: str, oauth_id: str, oauth_secret: str, group_id: str, room_id: str):
        self.capabilities_url = capabilities_url
        self.oauth_id = oauth_id
        self.oauth_secret = oauth_secret
        self.group_id = group_id
        self.room_id = room_id


class AuthResult:
    def __init__(self, user: User, room: Room):
        self.user = user
        self.room = room
