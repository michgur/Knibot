import re

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3

app = Flask(__name__)
help_cmd = 'עזרה'
help_msg = 'אהלן, אני קניבוט.\n פקודות:\n"עזרה": לקבלת הודעה זו\n"שלח": לשליחת הרשימה\n "תרשום": להוספת מוצרים לרשימה'
send_cmd = 'שלח'
write_cmd = 'תרשום'
write_msg = '📝'
writing = False
finish_cmd = 'זהו'
failed_msg = 'אופס חלה אצלי תקלה'


@app.route('/bot', methods=['POST'])
def bot():
    global writing
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    try:
        if help_cmd in incoming_msg:
            msg.body(help_msg)
        elif send_cmd in incoming_msg:
            conn = sqlite3.connect('./knibot.db')
            c = conn.cursor()
            c.execute('SELECT * FROM items')
            items = c.fetchall()
            msg.body('\n'.join(str(i) + ': ' + r[0] + ' (' + str(r[1]) + ')' for i, r in enumerate(items)))
            conn.close()
        elif write_cmd in incoming_msg:
            writing = True
            msg.body(write_msg)
        elif writing:
            if finish_cmd in incoming_msg:
                writing = False
                msg.body('אוקי')
            else:
                request_by = int(re.search(r'\d+', request.values.get('From')).group())
                conn = sqlite3.connect('./knibot.db')
                c = conn.cursor()
                c.execute('INSERT INTO items (name, request_by) VALUES (?, ?)',
                          (incoming_msg, request_by))
                conn.commit()
        else:
            msg.body(incoming_msg + ' you')
    except Exception as e:
        msg.body(failed_msg + ' ' + str(e))
    return str(resp)


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
