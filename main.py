import re

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from commands import KnibotInterpreter

app = Flask(__name__)


@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    user = int(re.search(r'\d+', request.values.get('From')).group())
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(KnibotInterpreter.interpret(user, incoming_msg))
    return str(resp)


# todo:
#   SOMEWHAT DONE tidier restful code structure
#   SOMEWHAT DONE better command parsing using tokenization, not RE
#   DONE manage different users & lists
#   inform users when their items are bought
#   look into whatsapp message formatting for cooler interface
#   deploy to an actual server

if __name__ == '__main__':
    app.run()
