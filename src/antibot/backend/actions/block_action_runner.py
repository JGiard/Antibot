import re
from typing import Type, Callable, Iterable

from autovalue import autovalue
from pyckson import parse
from pynject import pynject, singleton

from antibot.backend.constants import BLOCK_ACTION_OPTIONS
from antibot.backend.descriptor import find_method_by_attribute
from antibot.backend.endpoint_runner import EndpointRunner
from antibot.model.plugin import AntibotPlugin
from antibot.repository.users import UsersRepository
from antibot.slack.api import SlackApi
from antibot.slack.callback import BlockPayload
from antibot.slack.channel import Channel
from antibot.slack.message import Message


@autovalue
class BlockActionDescriptor:
    def __init__(self, plugin: Type[AntibotPlugin], method: Callable, block_id: str, action_id: str):
        self.plugin = plugin
        self.method = method
        self.block_id = block_id
        self.action_id = action_id


@pynject
@singleton
class BlockActionRunner:
    def __init__(self, endpoints: EndpointRunner, users: UsersRepository, api: SlackApi):
        self.endpoints = endpoints
        self.users = users
        self.api = api
        self.block_actions = []

    def install_plugin(self, plugin: Type[AntibotPlugin]):
        for method, options in find_method_by_attribute(plugin, BLOCK_ACTION_OPTIONS):
            self.block_actions.append(BlockActionDescriptor(plugin, method, options.block_id, options.action_id))

    def find_block_action(self, block_id: str, action_id: str) -> Iterable[BlockActionDescriptor]:
        for block_action in self.block_actions:
            if block_action.block_id is not None:
                if block_action.block_id == block_id or re.match(block_action.block_id, block_id):
                    yield block_action
                    continue
            if block_action.action_id is not None:
                if block_action.action_id == action_id or re.match(block_action.action_id, action_id):
                    yield block_action
                    continue

    def run_callback(self, payload: dict):
        message = parse(BlockPayload, payload)
        for action in message.actions:
            for block_action in self.find_block_action(action.block_id, action.action_id):
                user = self.users.get_user(message.user.id)
                channel = Channel(message.channel.id, message.channel.name)
                reply = self.endpoints.run(block_action.plugin, block_action.method,
                                           user=user, channel=channel,
                                           action=action, trigger_id=message.trigger_id,
                                           timestamp=message.container.message_ts,
                                           response_url=message.response_url)

                if isinstance(reply, Message):
                    self.api.respond(message.response_url, reply)