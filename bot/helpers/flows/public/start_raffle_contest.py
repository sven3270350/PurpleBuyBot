# TODO: /start_buy_contest  & /raffle_on -> Steps
# 1. Enter minimum amount in (USD)
# 2. Enter start time
# 3. Enter end time
# 4. Show countdown
# 5. Start contest

from telegram.ext import CallbackContext
from telegram.utils import helpers
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from services.bot_service import BotService
from helpers.utils import is_private_chat, is_group_admin
from helpers.templates import start_template, start_template_private, start_added_to_group