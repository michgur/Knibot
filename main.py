import re

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from groups import *
import prompts

app = Flask(__name__)
writing = False
write_re = re.compile(r'%s\s+([a-zA-Z0-9-_\u05D0-\u05EA]*)' % prompts.write_cmd)
instead_re = re.compile(r'%s\s+([a-zA-Z0-9-_\u05D0-\u05EA]*)' % prompts.instead_cmd)
remove_re = re.compile(r'%s\s+([a-zA-Z0-9-_\u05D0-\u05EA]*)' % prompts.remove_cmd)
list_re = re.compile(r'%s\s+([a-zA-Z0-9-_\u05D0-\u05EA]*)' % prompts.list_cmd)
new_re = re.compile(r'%s\s+([a-zA-Z0-9-_\u05D0-\u05EA]*)' % prompts.new_cmd)


def bot_test(user, incoming_msg):
    msg = ''
    try:
        new_match = new_re.search(incoming_msg)
        if new_match is not None:
            list_name = new_match.group(1)
            create_list(user, list_name)
            incoming_msg = new_re.sub(list_name, incoming_msg)
            msg = prompts.new_msg % list_name
        list_match = list_re.search(incoming_msg)
        if list_match is not None:
            list_name = list_match.group(1)
            set_working_list(user, list_name)
            msg += prompts.list_msg % list_name if msg == '' else prompts.new_list_msg
    except Exception as e:
        msg = str(e)
    finally:
        resp = MessagingResponse()
        resp.message().body(msg)
        print(msg)
        return str(resp)


@app.route('/bot', methods=['POST'])
def bot():
    global writing
    incoming_msg = request.values.get('Body', '').lower()
    user = int(re.search(r'\d+', request.values.get('From')).group())
    resp = MessagingResponse()
    msg = resp.message()
    try:
        if prompts.debug_cmd in incoming_msg:
            print(incoming_msg)
            msg.body('received debug info')
        elif prompts.help_cmd in incoming_msg:
            msg.body(prompts.help_msg)
        elif prompts.send_cmd in incoming_msg:
            items_raw = get_list_items(user)
            items = '\n'.join(str(i + 1) + ': ' + r[0] + ' (' + str(r[1]) + ')'
                              for i, r in enumerate(items_raw))
            msg.body(prompts.send_msg + items if items != '' else 'הרשימה ריקה')
        elif prompts.write_cmd in incoming_msg:
            writing = True
            msg.body(prompts.write_msg)
        elif prompts.bought_cmd in incoming_msg:
            remove_all_items(user)
            msg.body(prompts.bought_msg)
        elif writing:
            if prompts.finish_cmd in incoming_msg:
                writing = False
                msg.body('אוקי')
            else:
                add_items(user, incoming_msg)
        else:
            msg.body(incoming_msg + ' you')
    except Exception as e:
        msg.body(prompts.failed_msg + ' ' + str(e))
    return str(resp)


# todo:
#   tidier restful code structure
#   better command parsing using re. a clear & uniform syntax for different commands
#   manage different users & lists
#   look into whatsapp message formatting for cooler interface
#   deploy to an actual server

if __name__ == '__main__':
    print(bot_test(100, 'חדשה חברים'))
