import re

from flask import Flask, request
import telegram

import interpreter
import prompts_he

TOKEN = '1442387838:AAHjXPrVTaQiWQaeE-orOaccctdfvvxORvo'
username = 'kniyot_bot'
URL = 'https://82f7ed91a857.ngrok.io/'

bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)


@app.route('/%s' % TOKEN, methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    incoming_msg = update.message.text.encode('utf-8').decode().lower()
    user = update.message.from_user.id

    print(incoming_msg)
    resp_text = interpreter.run_command(bot, user, incoming_msg) \
        if incoming_msg != '/start' else prompts_he.greet_msg
    if resp_text:
        bot.send_message(chat_id=user, parse_mode='HTML', text=resp_text)

    return 'ok'


@app.route('/setwebhook', methods=['POST', 'GET'])
def set_webhook():
    s = bot.set_webhook('%s%s' % (URL, TOKEN))
    return 'setup successful' if s else 'setup failed'


@app.route('/')
def index():
    return 'i\'m alive'

# todo:
#   inform users when their items are bought
#   look into telegram message formatting for cooler interface
#   deploy to an actual server


if __name__ == '__main__':
    print('enter %ssetwebhook' % URL)
    app.run()
