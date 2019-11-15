from typing import Optional

from antibot.backend.constants import CMD_ATTR, JOB_ATTR_DAILY, WS_ATTR, WS_JSON_VALUES, BLOCK_ACTION_OPTIONS, \
    DIALOG_SUBMIT_ID, DIALOG_CANCEL_ID, CALLBACK_ID_REGEX, VIEW_CLOSED_ID, VIEW_SUBMIT_ID
from antibot.backend.descriptor import CommandDescriptor, WsDescriptor, BlockActionOptions


def command(route):
    def decorator(f):
        setattr(f, CMD_ATTR, CommandDescriptor(route, f))
        return f

    return decorator


def callback(id_regex):
    def decorator(f):
        setattr(f, CALLBACK_ID_REGEX, id_regex)
        return f

    return decorator


def block_action(block_id: Optional[str] = None, action_id: Optional[str] = None):
    def decorator(f):
        setattr(f, BLOCK_ACTION_OPTIONS, BlockActionOptions(block_id, action_id))
        return f

    return decorator


def dialog_submit(callback_id: str):
    def decorator(f):
        setattr(f, DIALOG_SUBMIT_ID, callback_id)
        return f

    return decorator


def dialog_cancel(callback_id: str):
    def decorator(f):
        setattr(f, DIALOG_CANCEL_ID, callback_id)
        return f

    return decorator


def view_closed(callback_id: str):
    def decorator(f):
        setattr(f, VIEW_CLOSED_ID, callback_id)
        return f

    return decorator


def view_submit(callback_id: str):
    def decorator(f):
        setattr(f, VIEW_SUBMIT_ID, callback_id)
        return f

    return decorator


def ws(route, method='POST'):
    def decorator(f):
        setattr(f, WS_ATTR, WsDescriptor(route, method, f))
        return f

    return decorator


def jsonobject():
    def decorator(f):
        setattr(f, WS_JSON_VALUES, True)
        return f

    return decorator


def daily(hour='00:00'):
    def decorator(f):
        setattr(f, JOB_ATTR_DAILY, hour)
        return f

    return decorator
