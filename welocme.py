import pytz


def welcome_message():
    message = """
    Hello! 👋 I'm your RemindMe 🤖, here to assist you!
Send me a message with your task 📝 with 'remind' keyword, for example, "remind Buy milk."
I will then ask you for the date 📅 and time ⏰, such as YYYY-MM-DD HH:MM or 'YYYY-MM-DD H:MMam/pm'
I'll set a reminder 🔔 for you to Buy milk at the specified time.
Keywords to use:
⌚ set: To set your timezone.
📋 menu: To see a list of keywords.
ℹ help: To view sample times for setting reminders.
📺 tutorial: To watch a tutorial on Youtube.
🪙 balance: To check your balance.
❌ cancel: Use this when asked for the time to start over.
By sending us a message, you agree to opt-in to the RemindMe Bot service.
"""
    return message



def set_message():
    # Get a list of all available timezones and sort them
    all_timezones = pytz.all_timezones
    all_timezones.sort()

    # Provide instructions to users
    message = f'''
    🌍 To set your time zone, please reply with keyword "set" and the name of your timezone like:
"set US/Pacific",
"set Europe/London",
"set Asia/Tokyo",
"set Asia/Kolkata,
"set Australia/Sydney",  
to see more https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568 
'''
    return message



def menu_message():
    message = '''
    ⚠Message the key terms in bold if you want to perform the action:
⌚ set: change to your time (Default: GMT+2)
ℹ help:  get sample times that you may use to set reminders
📺 tutorial: see tutorial on Youtube
🪙 balance: get your Subscription Plan and Reminder Tokens balance
❌ cancel: when you are asked to set the time and you want to restart the process by entering your task 
(Note: Once you get a reminder confirmation there is no going back)
    '''
    return message


def help_message():
    message = '''
    ⌚ Set your timezone once and only change if it changes.

    To set a reminder, message the bot with keyword 'remind' and the 'content' of the reminder.

    Tips:
    - Be specific; the bot learns from your usage.
    - Separate your message into an action.
    - Respond with the time, e.g., "remind Wash my clothes."
    - The bot will ask when to remind you.

    Sample answers:
    -remind Call mom.
    -remind Watch football.
    -remind Do assignment.

    After sending a non-one-word keyword, the bot will ask: 📅⏰: When should I remind you?

    Tips:
    -Enter the date and time for the reminder like this, 
    e.g., 
    -'2023-10-15 14:30' 
    -'2023-10-15 2:30am'
    -'2023-10-15 12:30pm'

    '''
    return message

def balance_message():
    message = "It's free to use."
    return message


def tutorial_message():
    message = "📺Till now we didn't post any video"
    return message


def cancle_message():
    message = '''
    📅⏰: What remind should I Cancle?
    An example of time would be cancle with keyword 'cancle'
    -'cancle Call mom.
    -'cancle Watch football' 
    -'cancle Do assignment.
    If one than one with same remind then it will delete recent one.
    '''
    return message