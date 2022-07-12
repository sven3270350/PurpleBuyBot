# TODO: /subscribe -> Steps
# 1. List available subscriptions plans
# 2. Allow user to select preferred subscription
# 3. Show wallet address for user
# 4. Allow user to confirm transaction
# 5. Check unique address for payment
# 6. Update user’s subscription

from telegram.ext import CallbackContext
from telegram.utils import helpers
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from services.bot_service import BotService
from helpers.utils import is_private_chat, is_group_admin
from helpers.templates import start_template, start_template_private, start_added_to_group

