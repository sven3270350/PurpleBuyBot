from telegram import Update, ParseMode
from telegram.ext import CallbackContext, Dispatcher, ConversationHandler, CommandHandler, CallbackQueryHandler
from models import SupportedChain, SupportedExchange, SupportedPairs
from helpers.utils import is_private_chat, is_group_admin, send_typing_action, reset_chat_data, not_group_admin
from services.bot_service import BotService
from services.bot_service import BotService
from helpers.templates import help_template


class GeneralHandler:
    def __init__(self, dispatcher: Dispatcher):
        self.dispatcher = dispatcher
        self.__add_handlers()

    @send_typing_action
    def chains(self, update: Update, context: CallbackContext):

        if is_private_chat(update):
            supported_chains: list[SupportedChain] = BotService(
            ).get_supported_chains()
            message = '<b>Supported Chains:</b>\n\n'

            if len(supported_chains) == 0:
                message += '<i>No supported chains found.</i>'
            else:
                # loop through the supported chains and add them to the message with numbered list
                for chain in supported_chains:
                    message += f'<b>{chain.chain_name}</b>\n'

                    dexes: list[SupportedExchange] = BotService(
                    ).get_supported_dexes(chain.chain_id)
                    pairs: list[SupportedPairs] = BotService(
                    ).get_supported_pairs(chain.chain_id)

                    message += "⮕ <i><b>Dex: </b>" + \
                        ("{}, " * len(dexes)).format(*
                                                     [dex.exchange_name for dex in dexes]) + "</i>\n"
                    message += "⮕ <i><b>Pair: </b>" + ("{}, " * len(pairs)).format(
                        *[pair.pair_name for pair in pairs]) + "</i>\n\n"

            update.message.reply_text(message, parse_mode=ParseMode.HTML)

    def help(self, update: Update, context: CallbackContext):
        if is_private_chat(update):
            update.message.reply_text(help_template,
                                      parse_mode=ParseMode.HTML)

    def __add_handlers(self):
        self.dispatcher.add_handler(CommandHandler("chains", self.chains))
        self.dispatcher.add_handler(CommandHandler("help", self.help))
