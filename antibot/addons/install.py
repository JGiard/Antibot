from functools import partial

import requests
from bottle import route, request, redirect, static_file
from pyckson import parse, serialize
from pymongo.database import Database
from pynject import pynject

from antibot.addons.addon_runner import AddOnRunnerProvider
from antibot.domain.auth import AddOnInstallation
from antibot.addons.descriptors import AddOnDescriptor
from antibot.addons.dialog_runner import DialogRunner
from antibot.addons.glance_runner import GlanceRunner
from antibot.addons.panel_runner import PanelRunner
from antibot.addons.tokens import TokenProvider
from antibot.addons.ws_runner import WsRunner
from antibot.constants import ADDON_INSTALLATIONS_DB, ADDON_CAPABILITIES_DB
from antibot.domain.configuration import Configuration
from antibot.storage import Storage


@pynject
class AddOnInstaller:
    def __init__(self, runner_provider: AddOnRunnerProvider, db: Database, token_provider: TokenProvider,
                 configuration: Configuration):
        self.configuration = configuration
        self.token_provider = token_provider
        self.runner_provider = runner_provider
        self.auth_storage = Storage(ADDON_INSTALLATIONS_DB, db)
        self.capabilities_storage = Storage(ADDON_CAPABILITIES_DB, db)

    def install(self, addon: AddOnDescriptor) -> str:
        runner = self.runner_provider.get(addon)
        route(runner.descriptor_path)(lambda: runner.descriptor)
        route(runner.installed_path)(lambda: self.on_installed(addon))

        for glance in addon.glances:
            glance_runner = runner.get_glance_runner(glance)
            route(glance_runner.glance_path)(partial(GlanceRunner.run_ws, glance_runner))
            route(glance_runner.icon_path)(partial(static_file, glance.icon, self.configuration.static_dir))

        for panel in addon.panels:
            panel_runner = runner.get_panel_runner(panel)
            route(panel_runner.panel_path)(partial(PanelRunner.run_ws, panel_runner))

        for dialog in addon.dialogs:
            dialog_runner = runner.get_dialog_runner(dialog)
            route(dialog_runner.dialog_path)(partial(DialogRunner.run_ws, dialog_runner))

        for ws in addon.wss:
            ws_runner = runner.get_ws_runner(ws)
            route(ws_runner.ws_path, method=ws.http_method)(partial(WsRunner.run_ws, ws_runner))

        return runner.descriptor_path

    def on_installed(self, addon: AddOnDescriptor):
        installable_url = request.query.installable_url
        installation = parse(AddOnInstallation, requests.get(installable_url).json())
        self.auth_storage.save(addon.db_key(installation.room_id), serialize(installation))

        self.token_provider.refresh_token(addon, installation)

        redirect_url = request.query.redirect_url
        redirect(redirect_url)
