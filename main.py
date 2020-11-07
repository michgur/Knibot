from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3

app = Flask(__name__)
help_cmd = 'עזרה'
help_msg = 'אהלן, אני קניבוט.\n פקודות:\n"עזרה": לקבלת הודעה זו\n"שלח": לשליחת הרשימה\n "תרשום": להוספת מוצרים לרשימה'
send_cmd = 'שלח'
write_cmd = 'תרשום'
write_msg = '📝'


@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    if help_cmd in incoming_msg: msg.body(help_msg)
    elif send_cmd in incoming_msg:
        conn = sqlite3.connect('./knibot.db')
        c = conn.cursor()
        c.execute('SELECT * FROM items')
        items = c.fetchall()
        msg.body('\n'.join(str(i[0]) + ': ' + i[2] + ' (' + i[1] + ')' for i in items))
        conn.close()
    else: msg.body(incoming_msg + ' you')
    # return a quote
    # r = requests.get('https://api.quotable.io/random')
    # if r.status_code == 200:
    # msg.body(quote)
    # msg.media('https://cataas.com/cat')
    return str(resp)


if __name__ == '__main__':
    # conn = sqlite3.connect('./knibot.db')
    # c = conn.cursor()
    # c.execute('DROP TABLE IF EXISTS items')
    # c.execute('CREATE TABLE items ('
    #           'id INTEGER PRIMARY KEY,'
    #           'name TEXT NOT NULL,'
    #           'request_by INTEGER)')
    # c.execute('SELECT * FROM items')
    # items = c.fetchall()
    # print('\n'.join(str(i[0]) + ': ' + i[2] + ' (' + i[1] + ')' for i in items))
    # conn.commit()
    app.run()
