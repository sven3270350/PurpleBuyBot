from helpers.bots_imports import *
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from helpers.flows.public.start import StartBot
from models import db, TrackedToken
from helpers.utils import extract_params, is_private_chat
from services.bot_service import BotService
from services.biggest_buy_service import BiggestBuyService
from services.bot_service import BotService
from eth_utils import is_address
from helpers.templates import help_template


telegram_bot_token = config('PUBLIC_BOT_API_KEY')
telegram_admin_bot_token = config('ADMIN_BOT_API_KEY')
bot = telegram.Bot(token=telegram_bot_token)
# bot.setWebhook(
#     f"https://{'biggestbuybot'}.herokuapp.com/{telegram_admin_bot_token}")


updater = Updater(token=telegram_bot_token, use_context=True)
dispatcher = updater.dispatcher


def help(update: Update, context: CallbackContext):
    if is_private_chat(update):
        update.message.reply_text(help_template,
                                  parse_mode=ParseMode.HTML)


def add_tokens(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = update.message.text
    args = extract_params(message)

    if len(args) == 0:
        # no arg provided, request for token address
        context.bot.send_message(chat_id=chat_id, text=help_template,
                                 parse_mode=ParseMode.HTML)
    elif len(args) == 1:
        # one arg provided, check if it's a valid token address
        token_address = args[0]
        if is_address(token_address):
            tracked_tokens = TrackedToken(
                token_address=token_address,
                group_id=str(chat_id)
            )
            db.session.add(tracked_tokens)
            context.user_data['tracked_tokens'] = token_address
            # TODO: check if token is already tracked
            pass
        else:
            error_message = '<b>❌Invalid token address: </b>\n\n'
            error_message += f'<i>{token_address}</i>\n'
            error_message += '<i>Please provide a valid token address.</i>'
            update.message.reply_text(
                error_message, parse_mode=ParseMode.HTML)
    else:
        error_message = '<b>❌Invalid command params: </b>\n\n'
        error_message += 'Use command /add_token {token_address} or just /add_token then follow the prompt to complete'
        update.message.reply_text(
            error_message, parse_mode=ParseMode.HTML)


def remove_tokens(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=help_template,
                             parse_mode=ParseMode.HTML)


def list_tracked_tokens(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    tracked_tokens = BotService().get_tracked_tokens(chat_id)
    message = "<b>You're Tracking:</b>\n\n"
    print(db.session.query(TrackedToken).filter(
        TrackedToken.group_id == str(chat_id)).first())

    if len(tracked_tokens) == 0:
        message += '<i>You currently are not tracking any tokens.</i>\n'
        message += '<i>Use the /add_tokens command to add tokens to your list.</i>'
        message += f"<i>{context.user_data['tracked_tokens']}</i>"

    else:
        # loop through the supported chains and add them to the message with numbered list
        for token in tracked_tokens:
            message += f"<b>{token.token_symbol} on {token.token_name}</b>\n"
            message += f" <i>{token.token_address}</i>\n"
            message += f" <i>{token.pair_address}</i>\n"

    update.message.reply_text(message, parse_mode=ParseMode.HTML)


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


def chains(update: Update, context: CallbackContext):
    supported_chains = BotService().get_supported_chains()
    message = '<b>Supported Chains:</b>\n\n'

    if len(supported_chains) == 0:
        message += '<i>No supported chains found.</i>'
    else:
        # loop through the supported chains and add them to the message with numbered list
        for chain in supported_chains:
            message += f'{chain.chain_name}\n'
    update.message.reply_text(message, parse_mode=ParseMode.HTML)


# call handlers for start commands
StartBot().call_start_handlers(dispatcher)

# handlers for the commands
dispatcher.add_handler(CommandHandler("help", help))
dispatcher.add_handler(CommandHandler("add_token", add_tokens))
dispatcher.add_handler(CommandHandler("remove_tokens", remove_tokens))
dispatcher.add_handler(CommandHandler("tracked_tokens", list_tracked_tokens))
dispatcher.add_handler(CommandHandler("buy_contest", start_buy_contest))
dispatcher.add_handler(CommandHandler("raffle_contest", start_raffle_contest))
dispatcher.add_handler(CommandHandler("subscribe", subscribe))
dispatcher.add_handler(CommandHandler("chains", chains))

#
updater.start_polling()
updater.idle()
