import os
from typing import List, Type

from injector import Module, Binder, singleton, inject, NoScope
from pymongo.database import Database
from pymongo.mongo_client import MongoClient
from slack_sdk import WebClient

from antibot.internal.configuration import Configuration
from antibot.internal.plugins import PluginsCollection
from antibot.plugin import AntibotPlugin


def configuration_provider() -> Configuration:
    return Configuration(bot_user_oauth_token=os.environ['SLACK_BOT_USER_TOKEN'],
                         signing_secret=os.environ['SIGNING_SECRET'],
                         ws_api_key=os.environ['WS_API_KEY'],
                         vhost=os.environ.get('VHOST', 'http://localhost:5001'),
                         prod=not os.environ.get('DEV', False))


@inject
def slack_client_provider(configuration: Configuration) -> WebClient:
    return WebClient(configuration.bot_user_oauth_token)


class AntibotModule(Module):
    def __init__(self, plugins: List[Type[AntibotPlugin]], submodules: List[Type[Module]]):
        self.plugins = plugins
        self.submodules = submodules

    def configure(self, binder: Binder):

        for plugin in self.plugins:
            binder.bind(plugin, scope=singleton)

        binder.bind(Configuration, to=configuration_provider)
        binder.bind(WebClient, to=slack_client_provider)
        binder.bind(PluginsCollection, to=PluginsCollection(self.plugins))

        binder.bind(Database, to=MongoClient(os.environ['MONGO_URI'])['antibot'], scope=NoScope)

        for module in self.submodules:
            binder.install(module())
