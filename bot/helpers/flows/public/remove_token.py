# TODO: /remove_tokens -> Steps
# 1. List all tracked tokens
# 2. Allow user to select token to delete
# 3. Show confirmation message
# 4. Delete from DB

from telegram.ext import CallbackContext
from telegram.utils import helpers
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from services.bot_service import BotService
from helpers.utils import is_private_chat, is_group_admin
from helpers.templates import start_template, start_template_private, start_added_to_group