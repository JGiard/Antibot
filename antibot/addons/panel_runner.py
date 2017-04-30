from bottle import abort, response

from antibot.addons.auth import AuthChecker
from antibot.addons.descriptors import AddOnDescriptor, PanelDescriptor
from antibot.domain.configuration import Configuration
from pynject import pynject, Injector


class PanelRunner:
    def __init__(self, instance, configuration: Configuration, auth: AuthChecker, addon: AddOnDescriptor,
                 panel: PanelDescriptor):
        self.auth = auth
        self.instance = instance
        self.addon = addon
        self.configuration = configuration
        self.panel = panel

    @property
    def descriptor(self):
        return {
            'name': {
                'value': self.panel.name
            },
            'url': self.configuration.base_url + self.panel_path,
            'key': self.panel.id,
            'location': 'hipchat.sidebar.right'
        }

    @property
    def panel_path(self) -> str:
        return '/{addon}/panel/{id}'.format(addon=self.addon.id, id=self.panel.id)

    def run_ws(self):
        if not self.auth.check_auth(self.addon):
            abort(401)
        response.set_header('Access-Control-Allow-Origin', '*')
        return self.run()

    def run(self):
        return self.panel.method(self.instance)


@pynject
class PanelRunnerProvider:
    def __init__(self, injector: Injector, configuration: Configuration, auth: AuthChecker):
        self.injector = injector
        self.auth = auth
        self.configuration = configuration

    def get(self, addon: AddOnDescriptor, panel: PanelDescriptor) -> PanelRunner:
        return PanelRunner(self.injector.get_instance(addon.cls), self.configuration, self.auth, addon, panel)
