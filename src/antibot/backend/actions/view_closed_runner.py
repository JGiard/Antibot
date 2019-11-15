from typing import Type, Callable, Iterable

from pyckson import parse
from pynject import pynject, singleton

from antibot.backend.constants import VIEW_CLOSED_ID
from antibot.backend.descriptor import find_method_by_attribute
from antibot.backend.endpoint_runner import EndpointRunner
from antibot.model.plugin import AntibotPlugin
from antibot.repository.users import UsersRepository
from antibot.slack.api import SlackApi
from antibot.slack.callback import ViewClosedPayload


class ViewClosedDescriptor:
    def __init__(self, plugin: Type[AntibotPlugin], method: Callable, callback_id: str):
        self.plugin = plugin
        self.method = method
        self.callback_id = callback_id


@pynject
@singleton
class ViewClosedRunner:
    def __init__(self, endpoints: EndpointRunner, users: UsersRepository, api: SlackApi):
        self.endpoints = endpoints
        self.users = users
        self.api = api
        self.descriptors = []

    def install_plugin(self, plugin: Type[AntibotPlugin]):
        for method, callback_id in find_method_by_attribute(plugin, VIEW_CLOSED_ID):
            self.descriptors.append(ViewClosedDescriptor(plugin, method, callback_id))

    def find_callback(self, callback_id) -> Iterable[ViewClosedDescriptor]:
        for descriptor in self.descriptors:
            if descriptor.callback_id == callback_id:
                yield descriptor

    def run(self, payload: dict):
        message = parse(ViewClosedPayload, payload)
        for descriptor in self.find_callback(message.view.callback_id):
            user = self.users.get_user(message.user.id)
            self.endpoints.run(descriptor.plugin, descriptor.method,
                               user=user, callback_id=message.view.callback_id,
                               private_metadata=message.view.private_metadata)
