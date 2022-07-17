from helpers.flows.public.add_token import AddToken
from helpers.flows.public.start import StartBot
from helpers.bots_imports import *
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from models import db, TrackedToken, SupportedChain, SupportedExchange, SupportedPairs
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


def remove_tokens(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=help_template,
                             parse_mode=ParseMode.HTML)


def list_tracked_tokens(update: Update, context: CallbackContext):
    group_id = context.chat_data.get('group_id', None)
    group_title = context.bot.get_chat(group_id).title

    if is_private_chat(update):
        if not BotService().is_group_in_focus(update, context):
            return

        tracked_tokens: list[TrackedToken] = BotService(
        ).get_tracked_tokens_by_group_id(group_id)
        message = f"<b>You're Tracking ({group_title}):</b>\n\n"

        if len(tracked_tokens) == 0:
            message += '<i>You currently are not tracking any tokens.</i>\n'
            message += '<i>Use the /add_tokens command to add tokens to your list.</i>'

        else:
            # loop through the supported chains and add them to the message with numbered list
            for token in tracked_tokens:
                message += f"<b>{token.token_name} on {token.chain_name}</b>\n"
                message += f"<i><b>Token Address: </b>{token.token_address}</i>\n"
                message += f"<i><b>Pair Address: </b>{token.pair_address}</i>\n"
                message += f"<i><b>Pair: </b>{token.pair_symbol}</i>\n"
                message += f"<i><b>Dex: </b>{token.exchange_name}</i>\n\n"

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
    supported_chains: list[SupportedChain] = BotService(
    ).get_supported_chains()
    message = '<b>Supported Chains:</b>\n\n'

    if is_private_chat(update):

        if len(supported_chains) == 0:
            message += '<i>No supported chains found.</i>'
        else:
            # loop through the supported chains and add them to the message with numbered list
            for chain in supported_chains:
                message += f'<b>{chain.chain_name}</b>\n'

                dexes: list[SupportedExchange] = BotService(
                ).get_supported_dexes(chain.id)
                pairs: list[SupportedPairs] = BotService(
                ).get_supported_pairs(chain.id)

                message += "⮕ <i><b>Dex: </b>" + \
                    ("{}, " * len(dexes)).format(*
                                                 [dex.exchange_name for dex in dexes]) + "</i>\n"
                message += "⮕ <i><b>Pair: </b>" + ("{}, " * len(pairs)).format(
                    *[pair.pair_name for pair in pairs]) + "</i>\n\n"

        update.message.reply_text(message, parse_mode=ParseMode.HTML)


# call handlers for start commands
StartBot().call_start_handlers(dispatcher)
AddToken(dispatcher)

# handlers for the commands
dispatcher.add_handler(CommandHandler("help", help))
dispatcher.add_handler(CommandHandler("remove_tokens", remove_tokens))
dispatcher.add_handler(CommandHandler("tracked_tokens", list_tracked_tokens))
dispatcher.add_handler(CommandHandler("buy_contest", start_buy_contest))
dispatcher.add_handler(CommandHandler("raffle_contest", start_raffle_contest))
dispatcher.add_handler(CommandHandler("subscribe", subscribe))
dispatcher.add_handler(CommandHandler("chains", chains))

#
updater.start_polling()
updater.idle()
