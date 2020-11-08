import prompts
from groups import *


def write(user, items_raw):
    if items_raw is not None:
        if prompts.instead_cmd in items_raw:
            instead_index = items_raw.index(prompts.instead_cmd)
            items = [i.strip() for i in items_raw[instead_index + len(prompts.instead_cmd):].split(',')
                     if not i.isspace()]
            remove_items(user, items)
            items_raw = items_raw[:instead_index - 1]
        items = [i.strip() for i in items_raw.split(',') if not i.isspace()]
        if len(items) == 0: return prompts.no_item_msg
        if prompts.instead_cmd in items:
            instead_index = items.index(prompts.instead_cmd)
            remove_items(user, items[instead_index + 1:])
            items = items[:instead_index]
        add_items(user, items)
    else:
        return prompts.no_item_msg
