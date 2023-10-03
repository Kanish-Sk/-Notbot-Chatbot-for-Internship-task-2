from flask import Flask, request
import pytz
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from utilis import cancle_remind, process_reminder, set_timezone
from welocme import balance_message, cancle_message, help_message, menu_message, set_message, tutorial_message, welcome_message


load_dotenv()

app = Flask(__name__)

mongo_uri = os.environ.get('MONGO_URI')

client = MongoClient(mongo_uri)

db_name = os.environ.get('DB_NAME')
users_collection_name = os.environ.get('USERS_COLLECTION')
reminders_collection_name = os.environ.get('REMINDERS_COLLECTION')

db = client[db_name]
users_collection = db[users_collection_name]
reminders_collection = db[reminders_collection_name]


@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        response = ''
        incoming_message = request.values.get('Body', '').lower()
        user_phone_number = request.values.get('From', '')

        user = users_collection.find_one({"phone_number": user_phone_number})
        if user and "timezone" in user:
            user_timezone = pytz.timezone(user["timezone"])
        else:
            user_timezone = None

        if incoming_message == 'remindme':
            response = welcome_message()

        elif incoming_message == "set":
            response = set_message()

        elif incoming_message == "menu":
            response = menu_message()

        elif incoming_message == "help":
            response = help_message()

        elif incoming_message == "tutorial":
            response = tutorial_message()

        elif incoming_message == "balance":
            response = balance_message()

        elif incoming_message == "cancle":
            response = cancle_message()

        else:
            if user_timezone:
                if incoming_message.startswith("set "):
                    response = set_timezone(
                        incoming_message, user_phone_number)

                elif incoming_message.startswith("cancle "):
                    response = cancle_remind(
                        incoming_message, user_phone_number)

                else:
                    response = process_reminder(
                        user, user_phone_number, incoming_message, user_timezone)

            else:
                response = set_timezone(incoming_message, user_phone_number)

        twiml_response = MessagingResponse()
        twiml_response.message(response)
        return str(twiml_response)

    except Exception as e:
        print(e)

        error_response = e
        twiml_response = MessagingResponse()
        twiml_response.message(error_response)
        return str(twiml_response)


if __name__ == '__main__':
    app.run(debug=True)
