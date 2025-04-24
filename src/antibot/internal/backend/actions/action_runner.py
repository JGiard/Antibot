import json

from bottle import request
from injector import singleton, inject

from antibot.internal.backend.actions.block_action_runner import BlockActionRunner
from antibot.internal.backend.actions.view_closed_runner import ViewClosedRunner
from antibot.internal.backend.actions.view_submit_runner import ViewSubmitRunner
from antibot.internal.backend.debugger import Debugger
from antibot.internal.backend.request_checker import RequestChecker
from antibot.repository.users import UsersRepository


@singleton
class ActionRunner:
    @inject
    def __init__(self, users: UsersRepository, checker: RequestChecker, block_actions: BlockActionRunner,
                 debugger: Debugger, view_closed: ViewClosedRunner, view_sumbit: ViewSubmitRunner):
        self.users = users
        self.block_actions = block_actions
        self.checker = checker
        self.debugger = debugger
        self.view_closed = view_closed
        self.view_sumbit = view_sumbit

    def run(self):
        self.checker.check_request(request)

        json_data = json.loads(request.forms['payload'])

        with self.debugger.wrap(json_data):
            if json_data['type'] == 'block_actions':
                return self.block_actions.run_callback(json_data)
            elif json_data['type'] == 'view_closed':
                return self.view_closed.run(json_data)
            elif json_data['type'] == 'view_submission':
                return self.view_sumbit.run(json_data)
            return None
