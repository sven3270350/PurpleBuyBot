from telegram.ext import CallbackContext, Dispatcher, ConversationHandler, CommandHandler, CallbackQueryHandler
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from services.bot_service import BotService
from helpers.utils import is_private_chat, is_group_admin, send_typing_action, reset_chat_data, not_group_admin
from helpers.templates import remove_token_confirmation_template, no_active_subscription_template, active_subscription_template
from models import TrackedToken, Subscription as SubscriptionModel, SubscriptionType

SELECT, CONFIRM, COMMIT = range(3)


class Subscription:
    def __init__(self, dispatcher: Dispatcher):
        self.dispatcher = dispatcher
        self.__add_handlers()

    @send_typing_action
    def __subscribe(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)

        if is_private_chat(update):
            if not BotService().is_group_in_focus(update, context):
                reset_chat_data(context)
                return ConversationHandler.END

            group_id = context.chat_data.get('group_id', None)
            context.chat_data['group_title'] = context.bot.get_chat(
                group_id).title
            chat_data: dict = context.chat_data

            if not is_group_admin(update, context):
                return not_group_admin(update)

            # show currect subscription plan
            active_subscriptions: list[SubscriptionModel] = BotService(
            ).get_active_active_subscription_by_group_id(group_id)

            if len(active_subscriptions) > 0:
                active_subscription: SubscriptionModel = active_subscriptions[0]

                # show current subscription plan
                update.message.reply_text(
                    text=active_subscription_template.format(
                        group_title=chat_data[
                            'group_title'],
                        package=f'{active_subscription.subscription_type} {"({active_subscription.total}}"}',
                        start_date=active_subscription.start_date,
                        end_date=active_subscription.end_date
                    ),
                    parse_mode=ParseMode.HTML)

                return ConversationHandler.END
            else:

                # show sumbscription plans
                plans: list[SubscriptionType] = BotService(
                ).get_subscription_plans()

                keyboard = []
                for plan in plans:
                    keyboard.append(
                        [InlineKeyboardButton(
                            f"{plan.subscription_type} (${plan.usd_price})",
                            callback_data=f"subscription_type:{plan.id}")])

                check_payment_button = InlineKeyboardButton(
                    "Check payment",
                    callback_data=f"check_payment:{group_id}")
                keyboard.append([check_payment_button])

                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text(
                    text=no_active_subscription_template.format(
                        group_title=chat_data['group_title']),
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML)

                return SELECT

        return ConversationHandler.END

    @send_typing_action
    def __select_subscription(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)
        chat_data = context.chat_data
        message_id = update.callback_query.message.message_id

        if not is_group_admin(update, context):
            return not_group_admin(update)

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

    @send_typing_action
    def __check_payment_status(self, update: Update, context: CallbackContext) -> int:
        pass

    def __confirm_subscripton(self, update: Update, context: CallbackContext):
        self.__extract_params(update, context)
        message_id = update.callback_query.message.message_id

        if not is_group_admin(update, context):
            return not_group_admin(update)
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
        self.dispatcher.add_handler(ConversationHandler(
            entry_points=[CommandHandler('subscribe', self.__subscribe)],
            states={
                SELECT: [CallbackQueryHandler(self.__select_subscription, pattern='^remove_token:\d+')],
                CONFIRM: [CallbackQueryHandler(
                    self.__confirm_subscripton, pattern='^confirm_removal:\d+')]
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
