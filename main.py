import re
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3
from groups import knibot_db

app = Flask(__name__)
greet_msg = '''שלום, אני קניבוט, בוט הקניות.🤖
אני עוזר לנהל רשימות קניות משותפות בין כמה משתתפים 📝.
מוצרים שיישלחו אלי ממך יופיעו לכל מי שמשתתף ברשימה שלך, וברגע שייקנו אותם אני אעדכן אותך.
כמה פקודות לשימוש בי:
✳️"תרשום"- להוספת פריטים לרשימה
✳️"שלח"- לשליחת הרשימה המלאה
✳️"קניתי"- לאיפוס הרשימה
✳️"תוריד"- להסרת פריטים מהרשימה'''
help_cmd = 'עזרה'
help_msg = 'אהלן, אני קניבוט.\n פקודות:\n"עזרה": לקבלת הודעה זו\n"שלח": לשליחת הרשימה\n "תרשום": להוספת מוצרים לרשימה'
send_cmd = 'שלח'
send_msg = 'הנה הרשימה:\n'
write_cmd = 'תרשום'
instead_cmd = 'במקום'
write_msg = 'אני רושם 📝. בסיום הרשימה נא לשלוח "זהו"'
writing = False
finish_cmd = 'זהו'
failed_msg = 'אופס חלה אצלי תקלה'
bought_cmd = 'קניתי'
bought_msg = 'סגור איפסתי את הרשימה'
remove_cmd = 'תוריד'
remove_msg = 'הסרתי את הפריטים'
debug_cmd = 'דבג'
write_re = re.compile(r'%s\s+([a-zA-Z0-9-_\u05D0-\u05EA]*)' % write_cmd)
instead_re = re.compile(r'%s\s+([a-zA-Z0-9-_\u05D0-\u05EA]*)' % instead_cmd)
remove_re = re.compile(r'%s\s+([a-zA-Z0-9-_\u05D0-\u05EA]*)' % remove_cmd)


@app.route('/bot', methods=['POST'])
def bot():
    global writing
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    try:
        if debug_cmd in incoming_msg:
            print(incoming_msg)
            msg.body('received debug info')
        elif help_cmd in incoming_msg:
            msg.body(help_msg)
        elif send_cmd in incoming_msg:
            with knibot_db.connect() as conn:
                c = conn.cursor()
                c.execute('SELECT * FROM items')
                items = '\n'.join(str(i + 1) + ': ' + r[0] + ' (' + str(r[1]) + ')'
                                  for i, r in enumerate(c.fetchall()))
            msg.body(send_msg + items if items != '' else 'הרשימה ריקה')
        elif write_cmd in incoming_msg:
            writing = True
            msg.body(write_msg)
        elif bought_cmd in incoming_msg:
            with knibot_db.connect(commit=True) as conn:
                c = conn.cursor()
                c.execute('DELETE FROM items')
            msg.body(bought_msg)
        elif writing:
            if finish_cmd in incoming_msg:
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
        msg.body(failed_msg + ' ' + str(e))
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
