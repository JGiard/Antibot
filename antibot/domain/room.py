from antibot.addons.descriptors import AddOnDescriptor


class Room:
    def __init__(self, jid, api_id, name, is_private: bool = False, addon: AddOnDescriptor = None):
        self.addon = addon
        self.is_private = is_private
        self.jid = jid
        self.api_id = api_id
        self.name = name
