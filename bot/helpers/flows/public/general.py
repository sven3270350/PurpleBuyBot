from telegram import Update, ParseMode
from telegram.ext import CallbackContext, Dispatcher, CommandHandler
from models import SupportedChain, SupportedExchange, SupportedPairs
from helpers.utils import is_private_chat, set_commands, send_typing_action, response_for_group
from services.bot_service import BotService
from services.bot_service import BotService
from helpers.templates import help_template


class GeneralHandler:
    def __init__(self, dispatcher: Dispatcher):
        self.dispatcher = dispatcher
        self.__add_handlers()

    @send_typing_action
    def __chains(self, update: Update, context: CallbackContext):
        self.__extract_params(update, context)

        if is_private_chat(update):
            supported_chains: list[SupportedChain] = BotService(
            ).get_supported_chains()
            set_commands(context, True)
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
        else:
            response_for_group(self, update)

    def __help(self, update: Update, context: CallbackContext):
        self.__extract_params(update, context)
        if is_private_chat(update):
            update.message.reply_text(help_template,
                                      parse_mode=ParseMode.HTML)
        else:
            response_for_group(self, update)

    def __add_handlers(self):
        self.dispatcher.add_handler(CommandHandler("chains", self.__chains))
        self.dispatcher.add_handler(CommandHandler("help", self.__help))

    def __extract_params(self, update: Update, context: CallbackContext):
        self.chattype = update.effective_chat.type
        self.chatid = str(update.effective_chat.id)
        self.chattitle = update.effective_chat.title
        self.chatusername = update.effective_chat.username
        self.group_message_sent_by = update.effective_user.username if update.effective_user.username else (
            update.message.from_user.username or None)
        self.bot_name = context.bot.username
