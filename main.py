from flask import Flask, request
import telegram
import os

import interpreter
from database import knibot_db

TOKEN = os.environ.get('TOKEN', None)
username = 'kniyot_bot'
URL = 'https://knibot.herokuapp.com/'

bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)


@app.route('/%s' % TOKEN, methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    user = update.message.from_user.id
    if update.message.text is not None:
        incoming_msg = update.message.text.encode('utf-8').decode().lower()
        interpreter.run_command(bot, user, incoming_msg)
    elif update.message.contact is not None:
        interpreter.add_contact(bot, user, update.message.contact)

    return 'ok'


@app.route('/setwebhook', methods=['POST', 'GET'])
def set_webhook():
    s = bot.set_webhook('%s%s' % (URL, TOKEN))
    return 'setup successful' if s else 'setup failed'


@app.route('/initdb', methods=['POST', 'GET'])
def init_db():
    try:
        knibot_db.create()
        return 'success'
    except Exception as e:
        return 'failure: ' + str(e)


@app.route('/cleardb', methods=['POST', 'GET'])
def clear_db():
    try:
        knibot_db.clear()
        return 'success'
    except Exception as e:
        return 'failure: ' + str(e)


@app.route('/')
def index():
    return 'i\'m alive'

# todo:
#   migrate to postgresql
#   add README
#   move on with your life
