from telegram.ext import CallbackContext
from telegram.utils import helpers
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from services.bot_service import BotService
from helpers.utils import is_private_chat, is_group_admin
from helpers.templates import start_template, start_template_private, start_added_to_group
from constants import ADD_BOT_TO_GROUP


class StartBot:

    def start(self, update: Update, context: CallbackContext):
        self.__extract_params(update, context)

        if is_private_chat(update):
            url = helpers.create_deep_linked_url(
                self.bot_name, ADD_BOT_TO_GROUP, group=True)
            button = InlineKeyboardMarkup.from_button(
                InlineKeyboardButton(text="Add bot to Group", url=url)
            )
            update.message.reply_text(text=start_template_private(self.bot_name),
                                      parse_mode=ParseMode.HTML, reply_markup=button)

        else:
            self.__response_for_group(update)

    def start_added_bot_to_group(self, update: Update, context: CallbackContext):
        self.__extract_params(update, context)
        if not is_private_chat(update):

            if BotService().is_registered_group(self.chatid):
                self.__response_for_group(update)
            else:
                try:
                    BotService().create_new_bot_user(self.chatid, self.chattitle, self.chatusername)
                    self.__response_for_group(update)

                except Exception as e:
                    print(f"Error creating new bot user: {e}")
                    update.message.reply_text(text="<i>❌ Error creating new bot user. Try again later</>",
                                              parse_mode=ParseMode.HTML)

    def start_as_group_owner(self, update: Update, context: CallbackContext):
        self.__extract_params(update, context)
        group_id = context.args[0]

        context.chat_data['group_id'] = group_id

        print(f"Chat data: {context.chat_data.get('group_id', None)}")

        if is_private_chat(update):
            if is_group_admin(update, context):
                update.message.reply_text(text=start_template,
                                          parse_mode=ParseMode.HTML)
            else:
                update.message.reply_text(text="<i>❌ You are not an admin of this group.</>",
                                        parse_mode=ParseMode.HTML)

    def __response_for_group(self, update: Update):
        url = helpers.create_deep_linked_url(
            self.bot_name, self.chatid)
        button = InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(text="Click me", url=url)
        )
        update.message.reply_text(text=start_added_to_group(self.bot_name),
                                  parse_mode=ParseMode.HTML, reply_markup=button)

    def __extract_params(self, update: Update, context: CallbackContext):
        self.chattype = update.effective_chat.type
        self.chatid = str(update.effective_chat.id)
        self.chattitle = update.effective_chat.title
        self.chatusername = update.effective_chat.username
        self.group_message_sent_by = update.effective_user.username
        self.bot_name = context.bot.username
