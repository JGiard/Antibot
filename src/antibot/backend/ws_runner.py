from bottle import request, abort
from pyckson import serialize
from pynject import Injector, pynject
from typing import Type

from antibot.model.configuration import Configuration
from antibot.model.plugin import AntibotPlugin


@pynject
class WsRunner:
    def __init__(self, injector: Injector, configuration: Configuration):
        self.injector = injector
        self.configuration = configuration

    def run_ws(self, method, plugin: Type[AntibotPlugin], **kwargs):
        if self.configuration.ws_api_key != request.params['apikey']:
            abort(401, 'Could not verify api key')
        if len(self.configuration.ws_ip_restictions) > 0 \
                and request.headers['X-Forwarded-For'] not in self.configuration.ws_ip_restictions:
            abort(401, 'Unauthorized IP')
        instance = self.injector.get_instance(plugin)

        reply = method(instance, **kwargs)
        if reply is not None:
            if isinstance(reply, dict):
                return reply
            else:
                return serialize(reply)
