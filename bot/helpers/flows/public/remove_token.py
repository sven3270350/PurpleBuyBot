from telegram.ext import CallbackContext, Dispatcher, ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram.utils import helpers
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from services.bot_service import BotService
from helpers.utils import is_private_chat, is_group_admin, send_typing_action, reset_chat_data
from helpers.templates import remove_token_confirmation_template
from models import TrackedToken
from helpers.flows.public.add_token import AddToken

SELECT, CONFIRM, COMMIT = range(3)


class RemoveToken:
    def __init__(self, dispatcher: Dispatcher):
        self.dispatcher = dispatcher
        self.__add_handlers()

    @send_typing_action
    def list_tracked_tokens(self, update: Update, context: CallbackContext):
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

    @send_typing_action
    def remove_token(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)
        group_id = context.chat_data.get('group_id', None)

        context.chat_data['group_title'] = context.bot.get_chat(group_id).title

        chat_data: dict = context.chat_data

        if is_private_chat(update):
            if not BotService().is_group_in_focus(update, context):
                reset_chat_data(context)
                return ConversationHandler.END

            if not is_group_admin(update, context):
                return AddToken().__not_group_admin(update, context)

            # list tracked tokens
            tracked_tokens: list[TrackedToken] = BotService(
            ).get_tracked_tokens_for_removal(group_id)

            if len(tracked_tokens) == 0:
                update.message.reply_text(
                    text="<i> ❌ No token is being tracked. Use /add_token to get started. </i>",
                    parse_mode=ParseMode.HTML)

                reset_chat_data(context)
                return ConversationHandler.END
            else:
                # list tracked tokens
                keyboard = []
                for token in tracked_tokens:
                    keyboard.append(
                        [InlineKeyboardButton(
                            f"{token.token_name} on {token.chain_name}",
                            callback_data=f"remove_token:{token.id}")])

                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text(
                    text=f"<i>Select a token to remove <b>({chat_data['group_title']})</b>:</i>",
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML)

                return SELECT

        return ConversationHandler.END

    @send_typing_action
    def select_token_to_remove(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)
        chat_data = context.chat_data
        message_id = update.callback_query.message.message_id

        if not is_group_admin(update, context):
            return AddToken().__not_group_admin(update, context)

        update.callback_query.answer()
        query = update.callback_query.data
        token_id = query.split(':')[1]
        context.chat_data['token_id'] = token_id

        token: TrackedToken = BotService().get_tracked_token_by_id(token_id)

        button = InlineKeyboardButton(
            text="Confirm",
            callback_data=f"confirm_removal:{token.id}")

        context.bot.edit_message_text(
            remove_token_confirmation_template.format(
                group_title=chat_data['group_title'],
                token_name=token.token_name,
                token_address=token.token_address,
                chain_name=token.chain[0].chain_name),
            chat_id=self.chatid,
            message_id=message_id,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[button]]))
        return CONFIRM

    def confirm_token_removal(self, update: Update, context: CallbackContext):
        self.__extract_params(update, context)
        message_id = update.callback_query.message.message_id

        if not is_group_admin(update, context):
            return AddToken().__not_group_admin(update, context)
        # BotService().delete_tracked_token(token_id)

        update.callback_query.answer()
        query = update.callback_query.data
        token_id = query.split(':')[1]
        context.chat_data['token_id'] = token_id

        BotService().delete_tracked_token(token_id)

        context.bot.edit_message_text(
            text=f"<i>✅ Token removed successfully!</i>",
            chat_id=self.chatid,
            message_id=message_id,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[]]))

        return ConversationHandler.END

    @ send_typing_action
    def __cancel_remove_token(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text(text="<i>❌ Remove Token Cancelled. </i>",
                                  parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    def __add_handlers(self):
        self.dispatcher.add_handler(CommandHandler(
            "tracked_tokens", self.list_tracked_tokens))
        self.dispatcher.add_handler(ConversationHandler(
            entry_points=[CommandHandler('remove_token', self.remove_token)],
            states={
                SELECT: [CallbackQueryHandler(self.select_token_to_remove, pattern='^remove_token:\d+')],
                CONFIRM: [CallbackQueryHandler(
                    self.confirm_token_removal, pattern='^confirm_removal:\d+')]
            },
            fallbacks=[CommandHandler('cancel', self.__cancel_remove_token)],
            conversation_timeout=300,
            name='remove_token'
        ))

    def __extract_params(self, update: Update, context: CallbackContext):
        self.chattype = update.effective_chat.type
        self.chatid = str(update.effective_chat.id)
        self.chattitle = update.effective_chat.title
        self.chatusername = update.effective_chat.username
        self.group_message_sent_by = update.effective_user.username
        self.bot_name = context.bot.username
