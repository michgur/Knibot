import re

from flask import Flask, request
import telegram

import interpreter
import prompts

TOKEN = '1442387838:AAGMYfzYDTDhAPN8cCznPlvpqtA22-tvKMI'
username = 'kniyot_bot'
URL = 'https://102d0414e1c5.ngrok.io/'

bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)


@app.route('/%s' % TOKEN, methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    incoming_msg = update.message.text.encode('utf-8').decode().lower()
    chat_id = update.message.chat_id
    user = update.message.from_user.id

    resp_text = interpreter.run_command(user, incoming_msg)\
        if incoming_msg != '/start' else prompts.greet_msg
    if resp_text:
        bot.send_message(chat_id=chat_id, text=resp_text)

    return 'ok'


@app.route('/setwebhook', methods=['POST', 'GET'])
def set_webhook():
    s = bot.set_webhook('%s%s' % (URL, TOKEN))
    return 'setup successful' if s else 'setup failed'


@app.route('/')
def index():
    return 'i\'m alive'

# todo:
#   SOMEWHAT DONE tidier restful code structure
#   SOMEWHAT DONE better command parsing using tokenization, not RE
#   DONE manage different users & lists
#   inform users when their items are bought
#   look into whatsapp message formatting for cooler interface
#   deploy to an actual server


if __name__ == '__main__':
    app.run()
