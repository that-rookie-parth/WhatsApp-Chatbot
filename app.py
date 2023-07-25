from flask import Flask, request
from utils import send_message
from utils import get_response

app = Flask(__name__)

@app.route('/')
def home():
    return 'No errors...'

@app.route('/twilio/receiveMessage', methods=['POST'])
def receiveMessage():
    try:
        # Extract incomng parameters from Twilio
        message = request.form['Body']
        sender_id = request.form['From']

        result = get_response(message)
        # result = text_complition(message)
        if result['status'] == 1:
            send_message(sender_id, result['response'])
    except:
        pass
    return 'OK', 200