from helpers.flows.public.subscription import Subscription
from helpers.flows.public.remove_token import RemoveToken
from helpers.flows.public.add_token import AddToken
from helpers.flows.public.start import StartBot
from helpers.flows.public.general import GeneralHandler
from helpers.bots_imports import *
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from services.bot_service import BotService
from helpers.templates import help_template


telegram_bot_token = config('PUBLIC_BOT_API_KEY')
telegram_admin_bot_token = config('ADMIN_BOT_API_KEY')
bot = telegram.Bot(token=telegram_bot_token)
# bot.setWebhook(
#     f"https://{'biggestbuybot'}.herokuapp.com/{telegram_admin_bot_token}")


updater = Updater(token=telegram_bot_token, use_context=True)
dispatcher = updater.dispatcher


def start_buy_contest(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=help_template,
                             parse_mode=ParseMode.HTML)


def start_raffle_contest(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=help_template,
                             parse_mode=ParseMode.HTML)


def subscribe(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=help_template,
                             parse_mode=ParseMode.HTML)


# call handlers for start commands
StartBot(dispatcher)
AddToken(dispatcher)
RemoveToken(dispatcher)
Subscription(dispatcher)
GeneralHandler(dispatcher)


# handlers for the commands
dispatcher.add_handler(CommandHandler("buy_contest", start_buy_contest))
dispatcher.add_handler(CommandHandler("raffle_contest", start_raffle_contest))


#
updater.start_polling()
updater.idle()
