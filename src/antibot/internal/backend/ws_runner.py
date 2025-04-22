from typing import Type

from bottle import request, abort
from injector import inject, Injector
from pyckson import serialize

from antibot.internal.backend.constants import WS_JSON_VALUES, NO_AUTH
from antibot.internal.backend.debugger import Debugger
from antibot.internal.configuration import Configuration
from antibot.plugin import AntibotPlugin


class WsRunner:
    @inject
    def __init__(self, injector: Injector, configuration: Configuration, debugger: Debugger):
        self.injector = injector
        self.configuration = configuration
        self.debugger = debugger

    def run_ws(self, method, plugin: Type[AntibotPlugin], **kwargs):
        request_key = request.params.get('apikey') or request.headers.get('X-Gitlab-Token')
        if not getattr(method, NO_AUTH, False) and self.configuration.ws_api_key != request_key:
            abort(401, 'Could not verify api key')
        request.get_header('X-Forwarded-For', request.environ.get('REMOTE_ADDR'))
        instance = self.injector.get(plugin)

        with self.debugger.wrap(request.json):
            reply = method(instance, **kwargs)
            if reply is not None:
                if getattr(method, WS_JSON_VALUES, False):
                    return serialize(reply)
                return reply
