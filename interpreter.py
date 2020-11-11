import re

import prompts
from groups import *


NAME = 0
USER = 1
INDEX = 2
ITEM_LIST = 3
USER_LIST = 4
NUMBER = 5
SEND = 6
LIST = 7
NEW = 8
WRITE = 9
ERASE = 10
CANCEL = 11
ALL = 12
EXCEPT = 13
INSTEAD = 14
COMMA = 15
FINISH = 16
BOUGHT = 17

operators = {
    'שלח': SEND,
    'רשימה': LIST,
    'חדשה': NEW,
    'רשום': WRITE,
    'תרשום': WRITE,
    'מחק': ERASE,
    'תמחק': ERASE,
    'בטל': CANCEL,
    'הכול': ALL,
    'חוץ': EXCEPT,
    'במקום': INSTEAD,
    ',': COMMA,
    'זהו': FINISH,
    'קניתי': BOUGHT,
}
name_re = re.compile(r'[^,]+')
number_re = re.compile(r'\d+')


def _tokenize(msg):
    tokens = re.split(r'\s+|(,)', msg)
    name = ''
    for t in tokens:
        if not t:
            continue
        if t in operators:
            op = operators[t]
            if name != '':
                yield NAME, name
                name = ''
            if op != COMMA:
                yield op, t
        else:
            name_match = name_re.match(t)
            if name_match is not None:
                if name != '':
                    name += ' '
                name += name_match.group()
            else:
                if name != '':
                    yield NAME, name
                    name = ''
                number_match = number_re.match(t)
                if number_match is not None:
                    yield NUMBER, number_match.group()
                else:
                    raise ValueError('unknown token %s' % t)
    if name != '':
        yield NAME, name


def _list_string_hebrew(items):
    length = len(items)
    if length == 1:
        return items[0]
    else:
        return ', '.join(items[:-1]) + ' ' + prompts.vav + items[-1]


def _add_tokenized_items(user, tokens):
    cmds, items = zip(*tokens)
    if INSTEAD in cmds:
        instead_index = cmds.index(INSTEAD)
        remove_items(user, items[instead_index + 1:])
        items = items[:instead_index]
    existing = get_existing_items(user, items)
    non_existing = [i for i in items if i not in existing]
    add_items(user, non_existing)
    if len(existing) == 0:
        return ''
    else:
        return prompts.existing_item_err % _list_string_hebrew(existing)


def _remove_tokenized_items(user, tokens):
    cmds, items = zip(*tokens)
    if cmds[0] == ALL:
        if len(cmds) > 2 and cmds[1] == EXCEPT:
            if items[2].startswith(prompts.mem):
                items = list(items)
                items[2] = items[2][1:]
            remove_all_items_but(user, items[2:])
        else:
            remove_all_items(user)
    else:
        existing = get_existing_items(user, items)
        non_existing = [i for i in items if i not in existing]
        remove_items(user, existing)
        if len(non_existing) == 1:
            return prompts.non_existing_item_err % non_existing[0]
        elif len(non_existing) > 1:
            return prompts.non_existing_items_err % _list_string_hebrew(non_existing)
    return ''


def run_command(user, message):
    try:
        tokens = list(_tokenize(message))
        cmd = tokens[0][0]

        if cmd == NAME:
            state = get_working_state(user)
            if state == STATE_WRITING:
                return _add_tokenized_items(user, tokens)
            elif state == STATE_ERASING:
                return _remove_tokenized_items(user, tokens)
            else:
                return prompts.default_working_state_err

        if cmd == SEND:
            items_raw = get_list_items(user)
            items_text = '\n'.join(str(i + 1) + ': ' + r[0] + ' (' + str(r[2]) + ')'
                                   for i, r in enumerate(items_raw))
            return prompts.send_msg + items_text if items_text != '' else prompts.empty_list_err

        if cmd == LIST:
            if tokens[1][0] == NEW:
                create_list(user, tokens[2][1])
                set_working_list(user, tokens[2][1])
                return prompts.new_list_msg % tokens[2][1]
            else:
                set_working_list(user, tokens[1][1])
                return prompts.list_msg % tokens[1][1]

        if cmd == NEW:
            create_list(user, tokens[1][1])
            return prompts.new_msg % tokens[1][1]

        if cmd == WRITE:
            if len(tokens) == 1:
                set_working_state(user, STATE_WRITING)
                return prompts.write_msg
            else:
                return prompts.finish_write_msg + ' ' + \
                       _add_tokenized_items(user, tokens[1:])

        if cmd == ERASE:
            if len(tokens) == 1:
                set_working_state(user, STATE_ERASING)
                return prompts.remove_msg
            else:
                return prompts.finish_remove_msg + ' ' + \
                       _remove_tokenized_items(user, tokens[1:])

        if cmd == FINISH:
            state = get_working_state(user)
            set_working_state(user, STATE_DEFAULT)
            return prompts.finish_write_msg if state == STATE_WRITING else prompts.finish_remove_msg

        if cmd == BOUGHT:
            if len(tokens) == 1:
                tokens.append((ALL, ''))
            return prompts.bought_msg + ' ' + \
                   _remove_tokenized_items(user, tokens[1:])

    except Exception as e:
        return str(e)
    return ''


if __name__ == '__main__':
    print(run_command(972502057283, 'תמחק חציל, אביר'))
