import pytz
import difflib
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from twilio.rest import Client

load_dotenv()

twilio_account_sid = os.environ.get('TWILIO_SID')
twilio_auth_token = os.environ.get('TWILIO_TOKEN')

twilio_number = os.environ.get('TWILIO_NUMBER')
twilio_client = Client(twilio_account_sid, twilio_auth_token)


mongo_uri = os.environ.get('MONGO_URI')

client = MongoClient(mongo_uri)

db_name = os.environ.get('DB_NAME')
users_collection_name = os.environ.get('USERS_COLLECTION')
reminders_collection_name = os.environ.get('REMINDERS_COLLECTION')

db = client[db_name]
users_collection = db.get_collection(users_collection_name)
reminders_collection = db.get_collection(reminders_collection_name)


temp_reminder_data = {}
message_to_remind = ''

scheduler = BackgroundScheduler()
scheduler.start()


def send_due_reminders():
    try:
        current_time_utc = datetime.datetime.now(pytz.UTC)

        due_reminders = reminders_collection.find(
            {"reminder_datetime": {"$lte": current_time_utc}})
        reminders_collection.delete_many(
            {"reminder_datetime": {"$lte": current_time_utc}})

        for reminder in due_reminders:
            print(reminder)
            user_phone_number = reminder["user_phone_number"]
            user_timezone = timezone(reminder["timezone"])
            reminder_datetime = reminder["reminder_datetime"].replace(
                tzinfo=pytz.UTC)
            current_time_user_tz = current_time_utc.astimezone(user_timezone)

            print(reminder_datetime, current_time_user_tz)

            if reminder_datetime <= current_time_user_tz:
                reminder_message = reminder["reminder_message"]

                print("Sending reminder message:", reminder_message)

                try:
                    twilio_client.messages.create(
                        body='🔔 ' + reminder_message,
                        from_=twilio_number,
                        to=user_phone_number
                    )
                    print(
                        f"Sent reminder to {user_phone_number}: {reminder_message}")

                except Exception as e:
                    print("Error sending reminder:", str(e))

    except Exception as e:
        print("Error in send_due_reminders:", str(e))


scheduler.add_job(
    send_due_reminders,
    trigger=CronTrigger(minute='*/1'),
    id='send_due_reminders'
)


def set_timezone(incoming_message, user_phone_number):
    if incoming_message.startswith("set "):
        user_timezone = incoming_message.split(" ", 1)[1].strip()
        all_timezones = pytz.all_timezones
        all_timezones.sort()
        closest_matches = difflib.get_close_matches(
            user_timezone, all_timezones)
        similarity_threshold = 0.8

        if closest_matches and difflib.SequenceMatcher(None, user_timezone, closest_matches[0]).ratio() >= similarity_threshold:
            matched_timezone = closest_matches[0]
            users_collection.update_one(
                {"phone_number": user_phone_number},
                {"$set": {"timezone": matched_timezone}},
                upsert=True
            )
            return f'''Timezone set to {matched_timezone}. 
You can now use other commands or
send reminder message uisng 'remind' keyword (eg. remind play cricket)
            '''
        else:
            return f'''
            Invalid TimeZone
Please reply with keyword "set" and the name of your timezone like: 
"set US/Pacific",
"set Europe/London",
"set Asia/Tokyo",
"set Asia/Kolkata,
"set Australia/Sydney",  
to see more https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568 
            '''

    return "Please set your time zone first using 'set'."


def process_reminder(user, user_phone_number, incoming_message, user_timezone):
    current_time_user_tz = datetime.datetime.now(user_timezone)

    if incoming_message.startswith("remind "):
        message_to_remind = incoming_message.split(" ", 1)[1].strip()
        temp_reminder_data[user_phone_number] = {
            "message": message_to_remind, "datetime": None}
        return "Please enter the date and time for the reminder, e.g., '2023-10-15 14:30' or '2023-10-15 2:30am' or '2023-10-15 12:30pm'"

    elif user_phone_number in temp_reminder_data:
        if temp_reminder_data[user_phone_number]["message"] or temp_reminder_data[user_phone_number]["datetime"] is None:
            flag = True
            try:
                try:
                    reminder_datetime = datetime.datetime.strptime(
                        incoming_message, '%Y-%m-%d %H:%M')
                except ValueError:
                    try:
                        flag = False
                        reminder_datetime = datetime.datetime.strptime(
                            incoming_message, '%Y-%m-%d %I:%M%p')
                        response_time = reminder_datetime.strftime(
                            '%Y-%m-%d %I:%M%p')
                        if "am" in incoming_message.lower():
                            reminder_datetime = reminder_datetime.replace(
                                hour=reminder_datetime.hour % 12)
                        elif "pm" in incoming_message.lower():
                            reminder_datetime = reminder_datetime.replace(
                                hour=(reminder_datetime.hour % 12) + 12)
                    except ValueError:
                        return "Invalid date and time format. Please use 'YYYY-MM-DD HH:MM' or 'YYYY-MM-DD H:MMam/pm'."

                reminder_datetime = user_timezone.localize(reminder_datetime)
                if flag:
                    response_time = reminder_datetime.strftime(
                        '%Y-%m-%d %H:%M')

                if reminder_datetime <= current_time_user_tz:
                    return '''The specified reminder datetime is in the past. Please set a future datetime.
To overcome this, check whether you are enter the time correctly.
                    '''

                reminders_collection.insert_one({
                    "user_phone_number": user_phone_number,
                    "reminder_datetime": reminder_datetime,
                    "reminder_message": temp_reminder_data[user_phone_number]["message"],
                    "timezone": user['timezone']
                })

                message = temp_reminder_data[user_phone_number]['message']

                del temp_reminder_data[user_phone_number]
                message_to_remind = ''

                return f"Your reminder message '{message}' is set for {response_time} "

            except ValueError as e:
                return str(e)

    temp_reminder_data[user_phone_number] = {"message": None, "datetime": None}
    return "Please send a reminder message using the 'remind' keyword, e.g., 'remind play cricket'."


def cancle_remind(incoming_message, user_phone_number):
    message_to_cancel = incoming_message.split(" ", 1)[1].strip()

    matching_reminders = list(reminders_collection.find({
        "user_phone_number": user_phone_number,
        "reminder_message": message_to_cancel
    }).sort("_id", -1))

    if matching_reminders:
        last_matching_reminder = matching_reminders[0]
        reminders_collection.delete_one({"_id": last_matching_reminder["_id"]})
        return f"Last reminder '{message_to_cancel}' canceled successfully."
    else:
        return "No reminder with that content exists."
