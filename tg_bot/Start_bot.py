import os

from dotenv import load_dotenv
from os.path import join, dirname

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import tg_bot.GC_TelegramBot as GC_TelegramBot


# Load .env & token for the bot
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
TLGR_TOKEN = os.environ.get('TLGR_TOKEN')

# Initialize updater and dispatcher
updater = Updater(token=TLGR_TOKEN)
dispatcher = updater.dispatcher

# define command handlers
bind_calendar_handler = CommandHandler('bind', GC_TelegramBot.add_calendar_callback)
cancel_handler = CommandHandler('cancel', GC_TelegramBot.chancel_callback)
start_handler = CommandHandler('start', GC_TelegramBot.start_callback)
help_handler = CommandHandler('help', GC_TelegramBot.help_callback)
unbind_calendar_handler = CommandHandler('unbind', GC_TelegramBot.unbind_calendar_callback)
logout_handler = CommandHandler('logout', GC_TelegramBot.logout_callback)

# define other handlers
message_handler = MessageHandler(Filters.text, GC_TelegramBot.handle_user_message)

# adding handlers to dispatcher
dispatcher.add_handler(bind_calendar_handler)
dispatcher.add_handler(cancel_handler)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(unbind_calendar_handler)
dispatcher.add_handler(logout_handler)


dispatcher.add_handler(message_handler)

# and start the bot...
updater.start_polling()