# TODO: /add_tokens -> Steps
# 1. Prompt user to select chain
# 2. Prompt user to select Dex
# 3. Prompt user to enter token address
# 4. Prompt user to select pair ?
# 5. Show summary of tokens to be tracked
# 6. Request for confirmation
# 7. Write to DB

from telegram.ext import CallbackContext
from telegram.utils import helpers
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from services.bot_service import BotService
from helpers.utils import is_private_chat, is_group_admin
from helpers.templates import start_template, start_template_private, start_added_to_group