import re

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from groups import knibot_db
import prompts

app = Flask(__name__)
writing = False
write_re = re.compile(r'%s\s+([a-zA-Z0-9-_\u05D0-\u05EA]*)' % prompts.write_cmd)
instead_re = re.compile(r'%s\s+([a-zA-Z0-9-_\u05D0-\u05EA]*)' % prompts.instead_cmd)
remove_re = re.compile(r'%s\s+([a-zA-Z0-9-_\u05D0-\u05EA]*)' % prompts.remove_cmd)


@app.route('/bot', methods=['POST'])
def bot():
    global writing
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    try:
        if prompts.debug_cmd in incoming_msg:
            print(incoming_msg)
            msg.body('received debug info')
        elif prompts.help_cmd in incoming_msg:
            msg.body(prompts.help_msg)
        elif prompts.send_cmd in incoming_msg:
            with knibot_db.connect() as conn:
                c = conn.cursor()
                c.execute('SELECT * FROM items')
                items = '\n'.join(str(i + 1) + ': ' + r[0] + ' (' + str(r[1]) + ')'
                                  for i, r in enumerate(c.fetchall()))
            msg.body(prompts.send_msg + items if items != '' else 'הרשימה ריקה')
        elif prompts.write_cmd in incoming_msg:
            writing = True
            msg.body(prompts.write_msg)
        elif prompts.bought_cmd in incoming_msg:
            with knibot_db.connect(commit=True) as conn:
                c = conn.cursor()
                c.execute('DELETE FROM items')
            msg.body(prompts.bought_msg)
        elif writing:
            if prompts.finish_cmd in incoming_msg:
                writing = False
                msg.body('אוקי')
            else:
                request_by = int(re.search(r'\d+', request.values.get('From')).group())
                with knibot_db.connect(commit=True) as conn:
                    c = conn.cursor()
                    c.execute('INSERT INTO items (name, request_by) VALUES (?, ?)',
                              (incoming_msg, request_by))
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
    # conn = sqlite3.connect('./knibot.db')
    # c = conn.cursor()
    # c.execute('DROP TABLE IF EXISTS items')
    # c.execute('CREATE TABLE items ('
    #           'name TEXT NOT NULL,'
    #           'request_by INTEGER)')
    # c.execute('SELECT * FROM items')
    # items = c.fetchall()
    # print('\n'.join(str(i[0]) + ': ' + i[2] + ' (' + i[1] + ')' for i in items))
    # conn.commit()
    app.run()
