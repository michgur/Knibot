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

    user = update.message.from_user.id
    if update.message.contact is not None:
        interpreter.add_contact(bot, user, update.message.contact)
        return 'ok'
    incoming_msg = update.message.text.encode('utf-8').decode().lower()

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
#   add buttons & user guidance
#   deploy to an actual server
#   add README
#   move on with your life


if __name__ == '__main__':
    print('enter %ssetwebhook' % URL)
    app.run()
