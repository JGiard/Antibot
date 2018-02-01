from bottle import abort, response
from pynject import pynject, Injector

from antibot.addons.auth import AuthChecker
from antibot.domain.auth import AuthResult
from antibot.addons.descriptors import AddOnDescriptor, WsDescriptor
from antibot.addons.tokens import TokenProvider
from antibot.addons.utils import addon_method_runner
from antibot.domain.configuration import Configuration
from antibot.domain.room import Room
from antibot.domain.user import User


class WsRunner:
    def __init__(self, instance, configuration: Configuration, auth: AuthChecker, token_provider: TokenProvider,
                 addon: AddOnDescriptor, ws: WsDescriptor):
        self.token_provider = token_provider
        self.auth = auth
        self.instance = instance
        self.addon = addon
        self.configuration = configuration
        self.ws = ws
        self.panel_key = None

    @property
    def ws_path(self) -> str:
        return self.ws.route

    def run_ws(self, **kwargs):
        auth = self.auth.check_auth(self.addon)
        if not auth:
            abort(401)
        response.set_header('Access-Control-Allow-Origin', '*')
        return self.run(auth.user, auth.room, kwargs)

    def run(self, user: User, room: Room, ws_params: dict = None):
        return addon_method_runner(self.ws.method, self.instance, user, room, ws_params)


@pynject
class WsRunnerProvider:
    def __init__(self, injector: Injector, configuration: Configuration, auth: AuthChecker,
                 token_provider: TokenProvider):
        self.injector = injector
        self.auth = auth
        self.configuration = configuration
        self.token_provider = token_provider

    def get(self, addon: AddOnDescriptor, ws: WsDescriptor) -> WsRunner:
        return WsRunner(self.injector.get_instance(addon.cls), self.configuration, self.auth,
                        self.token_provider, addon, ws)
