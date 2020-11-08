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
        if len(items) == 0: return prompts.no_item_msg
        add_items(user, items)
    else:
        return prompts.no_item_msg


def remove(user, items_raw):
    if items_raw is not None:
        items = [i.strip() for i in items_raw.split(',') if not i.isspace()]
        if len(items) == 0: return prompts.no_item_msg
        remove_items(user, items)
    else:
        return prompts.no_item_msg


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
        ',': COMMA
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


if __name__ == '__main__':
    print(*KnibotTokenizer.tokenize('שלח תרשום בננה, חציל, אגס'))
