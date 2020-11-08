import re

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

import commands
from groups import *
import prompts

app = Flask(__name__)
writing = False
write_re = re.compile(r'%s(\s+([^,]+,)*[^,]+)?' % prompts.write_cmd)
instead_re = re.compile(r'%s\s+([a-zA-Z0-9-_\u05D0-\u05EA]*)' % prompts.instead_cmd)
remove_re = re.compile(r'%s(\s+([^,]+,)*[^,]+)?' % prompts.remove_cmd)
list_re = re.compile(r'%s\s+([a-zA-Z0-9-_\u05D0-\u05EA]+)' % prompts.list_cmd)
new_re = re.compile(r'%s\s+([a-zA-Z0-9-_\u05D0-\u05EA]+)' % prompts.new_cmd)
items_re = re.compile(r'(([^,]+,)*[^,]+)?')


def bot_test(user, incoming_msg):
    global writing
    incoming_msg = re.sub(r'\s+', ' ', incoming_msg)
    msg = ''
    try:
        new_match = new_re.search(incoming_msg)
        if new_match is not None:
            list_name = new_match.group(1)
            create_list(user, list_name)
            incoming_msg = new_re.sub(list_name, incoming_msg)
            msg += (prompts.new_msg % list_name) + '\n'
        list_match = list_re.search(incoming_msg)
        if list_match is not None:
            list_name = list_match.group(1)
            set_working_list(user, list_name)
            msg += (prompts.list_msg % list_name if msg == '' else prompts.new_list_msg) + '\n'
        write_match = write_re.search(incoming_msg)
        if write_match is not None:
            items_raw = write_match.group(1)
            if items_raw is not None:
                exc = commands.write(user, items_raw)
                msg += (prompts.finish_msg if exc is None else exc) + '\n'
            else:
                msg += prompts.write_msg + '\n'
                writing = True
        elif writing and msg == '':
            if prompts.finish_cmd in incoming_msg:
                msg += prompts.finish_msg
                writing = False
            else:
                exc = commands.write(user, incoming_msg)
                if exc is not None:
                    msg += exc
        remove_match = remove_re.search(incoming_msg)
        if remove_match is not None:
            items_raw = remove_match.group(1)
            if items_raw is not None:
                exc = commands.write(user, items_raw)
                msg += (prompts.remove_msg if exc is None else exc) + '\n'
        if prompts.send_cmd in incoming_msg:
            items_raw = get_list_items(user)
            items_text = '\n'.join(str(i + 1) + ': ' + r[0] + ' (' + str(r[2]) + ')'
                                   for i, r in enumerate(items_raw))
            msg += (prompts.send_msg + items_text if items_text != '' else 'הרשימה ריקה') + '\n'
        if prompts.bought_cmd in incoming_msg:
            remove_all_items(user)
            msg += prompts.bought_msg + '\n'

    except Exception as e:
        msg = str(e)
    finally:
        return msg.strip()


@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    user = int(re.search(r'\d+', request.values.get('From')).group())
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(bot_test(user, incoming_msg))
    return str(resp)


# todo:
#   SOMEWHAT DONE tidier restful code structure
#   better command parsing using tokenization, not RE
#   DONE manage different users & lists
#   look into whatsapp message formatting for cooler interface
#   deploy to an actual server

if __name__ == '__main__':
    app.run()
