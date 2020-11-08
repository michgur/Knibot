import re

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
        if len(items) == 0: return prompts.no_item_err
        add_items(user, items)
    else:
        return prompts.no_item_err


def remove(user, items_raw):
    if items_raw is not None:
        items = [i.strip() for i in items_raw.split(',') if not i.isspace()]
        if len(items) == 0: return prompts.no_item_err
        remove_items(user, items)
    else:
        return prompts.no_item_err


class KnibotTokenizer:
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

    @classmethod
    def tokenize(cls, msg):
        tokens = re.split(r'\s+|(,)', msg)
        name = ''
        for t in tokens:
            if not t:
                continue
            if t in cls.operators:
                op = cls.operators[t]
                if name != '':
                    yield cls.NAME, name
                    name = ''
                if op != cls.COMMA:
                    yield op, t
            else:
                name_match = cls.name_re.match(t)
                if name_match is not None:
                    if name != '':
                        name += ' '
                    name += name_match.group()
                else:
                    if name != '':
                        yield cls.NAME, name
                        name = ''
                    number_match = cls.number_re.match(t)
                    if number_match is not None:
                        yield cls.NUMBER, number_match.group()
                    else:
                        raise ValueError('unknown token %s' % t)
        if name != '':
            yield cls.NAME, name

    @staticmethod
    def list_string_hebrew(items):
        length = len(items)
        if length == 1:
            return items[0]
        else:
            return ', '.join(items[:-1]) + ' ' + prompts.vav + items[-1]


class KnibotInterpreter:
    @staticmethod
    def add_tokenized_items(user, tokens):
        cmds, items = zip(*tokens)
        if KnibotTokenizer.INSTEAD in cmds:
            instead_index = cmds.index(KnibotTokenizer.INSTEAD)
            remove_items(user, items[instead_index + 1:])
            items = items[:instead_index]
        existing = get_existing_items(user, items)
        non_existing = [i for i in items if i not in existing]
        add_items(user, non_existing)
        if len(existing) == 0:
            return ''
        else:
            return prompts.existing_item_err % KnibotTokenizer.list_string_hebrew(existing)

    @staticmethod
    def remove_tokenized_items(user, tokens):
        cmds, items = zip(*tokens)
        if cmds[0] == KnibotTokenizer.ALL:
            if len(cmds) > 2 and cmds[1] == KnibotTokenizer.EXCEPT:
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
                return prompts.non_existing_items_err % KnibotTokenizer.list_string_hebrew(non_existing)
        return ''

    @staticmethod
    def interpret(user, message):
        try:
            tokens = list(KnibotTokenizer.tokenize(message))
            cmd = tokens[0][0]

            if cmd == KnibotTokenizer.NAME:
                state = get_working_state(user)
                if state == STATE_WRITING:
                    return KnibotInterpreter.add_tokenized_items(user, tokens)
                elif state == STATE_ERASING:
                    return KnibotInterpreter.remove_tokenized_items(user, tokens)
                else:
                    return prompts.default_working_state_err

            if cmd == KnibotTokenizer.SEND:
                items_raw = get_list_items(user)
                items_text = '\n'.join(str(i + 1) + ': ' + r[0] + ' (' + str(r[2]) + ')'
                                       for i, r in enumerate(items_raw))
                return prompts.send_msg + items_text if items_text != '' else prompts.empty_list_err

            if cmd == KnibotTokenizer.LIST:
                if tokens[1][0] == KnibotTokenizer.NEW:
                    create_list(user, tokens[2][1])
                    set_working_list(user, tokens[2][1])
                    return prompts.new_list_msg % tokens[2][1]
                else:
                    set_working_list(user, tokens[1][1])
                    return prompts.list_msg % tokens[1][1]

            if cmd == KnibotTokenizer.NEW:
                create_list(user, tokens[1][1])
                return prompts.new_msg % tokens[1][1]

            if cmd == KnibotTokenizer.WRITE:
                if len(tokens) == 1:
                    set_working_state(user, STATE_WRITING)
                    return prompts.write_msg
                else:
                    return prompts.finish_write_msg + ' ' + \
                           KnibotInterpreter.add_tokenized_items(user, tokens[1:])

            if cmd == KnibotTokenizer.ERASE:
                if len(tokens) == 1:
                    set_working_state(user, STATE_ERASING)
                    return prompts.remove_msg
                else:
                    return prompts.finish_remove_msg + ' ' + \
                           KnibotInterpreter.remove_tokenized_items(user, tokens[1:])

            if cmd == KnibotTokenizer.FINISH:
                state = get_working_state(user)
                set_working_state(user, STATE_DEFAULT)
                return prompts.finish_write_msg if state == STATE_WRITING else prompts.finish_remove_msg

            if cmd == KnibotTokenizer.BOUGHT:
                if len(tokens) == 1:
                    tokens.append((KnibotTokenizer.ALL, ''))
                return prompts.bought_msg + ' ' + \
                       KnibotInterpreter.remove_tokenized_items(user, tokens[1:])

        except Exception as e:
            return str(e)
        return ''


if __name__ == '__main__':
    print(KnibotInterpreter.interpret(972502057283, 'תמחק חציל, אביר'))
