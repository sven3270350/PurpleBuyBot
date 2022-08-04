from functools import wraps
from telegram import (ChatAction)
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, ConversationHandler
import json
from web3 import HTTPProvider, Web3
from services.bot_service import BotService
from helpers.app_config import AppConfigs
from helpers.templates import not_group_admin_template


def erc20Abi():
    with open("./erc20abi.json") as ABI:
        return json.dumps(json.load(ABI.read()))


def extract_params(params):
    """
    Extracts the parameters from a string. Skips the first word.
    """
    params = params.split(' ')
    params.pop(0)
    params = [param.strip() for param in params]
    return params


def is_group_admin(update: Update, context: CallbackContext):
    """
    Checks if the user is a group admin.
    """
    if context.chat_data.get('group_id'):
        return BotService().is_chat_admin(context, context.chat_data.get('group_id'), update.effective_user.id)
    return False


def is_private_chat(update: Update):
    """
    Checks if the chat is a private chat.
    """
    return update.effective_chat.type == 'private'


def send_typing_action(func):
    """Sends typing action while processing func command."""
    @wraps(func)
    def command_func(self, update, context, *args, **kwargs):
        if is_private_chat(update):
            context.bot.send_chat_action(
                chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(self, update, context,  *args, **kwargs)

    return command_func


def reset_chat_data(context: CallbackContext):
    group_id = context.chat_data.get('group_id', None)
    context.chat_data.clear()
    context.chat_data['group_id'] = group_id


def not_group_admin(update: Update, context: CallbackContext):
    update.message.reply_text(text=not_group_admin_template,
                              parse_mode=ParseMode.HTML)
    reset_chat_data(context)
    return ConversationHandler.END


class EventList(list):

    def __setitem__(self, key, value):
        super(EventList, self).__setitem__(key, value)
        print("The list has been changed!")

    def __delitem__(self, value):
        super(EventList, self).__delitem__(value)
        print("The list has been changed!")

    def __add__(self, value):
        super(EventList, self).__add__(value)
        print("The list has been changed!")

    def __iadd__(self, value):
        super(EventList, self).__iadd__(value)
        print("The list has been changed!")

    def append(self, value):
        super(EventList, self).append(value)
        print("The list has been changed!")

    def remove(self, value):
        super(EventList, self).remove(value)
