from telegram.ext import CallbackContext, Dispatcher, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram.utils import helpers
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from services.bot_service import BotService
from helpers.utils import is_private_chat, is_group_admin, send_typing_action, reset_chat_data, not_group_admin
from helpers.templates import (
    no_trackecd_tokens_template, start_biggest_buy_contest_template,
    set_start_time_template, set_end_time_template, set_min_buy_template,
    set_winner_reward_template, start_competition_confirmation_template,
    biggest_buy_competition_alert_template)
from datetime import datetime, timedelta

START_TIME, END_TIME, MIN_BUY, WINNER_PRIZE = range(4)

COMPETITION_NAME = "Raffle"


class RaffleContest:
    def __init__(self, dispatcher: Dispatcher):
        self.dispatcher = dispatcher
        self.__add_handlers()
        self.__create_handlers()

    @send_typing_action
    def __start(self, update: Update, context: CallbackContext):
        self.__extract_params(update, context)
        self.__set_button_handlers()

        if is_private_chat(update):
            if not BotService().is_group_in_focus(update, context):
                reset_chat_data(context)
                return ConversationHandler.END

            group_id = context.chat_data.get('group_id', None)
            context.chat_data['group_title'] = context.bot.get_chat(
                group_id).title

            if not is_group_admin(update, context):
                return not_group_admin(update)

            tracked_token = BotService().get_user_tracked_token_name(group_id)
            if not tracked_token:
                reset_chat_data(context)

                update.message.reply_text(
                    text=no_trackecd_tokens_template,
                    parse_mode=ParseMode.HTML
                )
                return ConversationHandler.END

            context.chat_data['tracked_token'] = tracked_token

            # Default setup
            start_time = datetime.now()+timedelta(minutes=30)
            end_time = start_time + timedelta(hours=2)

            context.chat_data['start_time'] = start_time.strftime('%H:%M:%S')
            context.chat_data['end_time'] = end_time.strftime('%H:%M:%S')
            context.chat_data['minimum_buy'] = '500'
            context.chat_data['winner_prize'] = '200'

            self.__reply_template(update, context)

            return START_TIME

    @send_typing_action
    def __set_start_time(self, update: Update, context: CallbackContext):
        self.__extract_params(update, context)
        timestring = update.message.text
        context.chat_data['start_time'] = timestring

        self.dispatcher.remove_handler(self.start_time_handler)
        self.__reply_template(update, context)
        return END_TIME

    @send_typing_action
    def __set_end_time(self, update: Update, context: CallbackContext):
        self.__extract_params(update, context)
        timestring = update.message.text
        context.chat_data['end_time'] = timestring

        self.dispatcher.remove_handler(self.end_time_handler)
        self.__reply_template(update, context)
        return MIN_BUY

    @send_typing_action
    def __set_min_buy(self, update: Update, context: CallbackContext):
        self.__extract_params(update, context)
        min_buy = update.message.text
        context.chat_data['minimum_buy'] = min_buy

        self.dispatcher.remove_handler(self.min_buy_handler)
        self.__reply_template(update, context)
        return WINNER_PRIZE

    @send_typing_action
    def __set_winner_prize(self, update: Update, context: CallbackContext):
        self.__extract_params(update, context)
        winner_prize = update.message.text
        context.chat_data['winner_prize'] = winner_prize

        self.dispatcher.remove_handler(self.winner_prize_handler)
        self.__reply_template(update, context)
        return START_TIME

    def __start_competition(self, update: Update, context: CallbackContext):
        self.__extract_params(update, context)

        if is_private_chat(update):
            if not BotService().is_group_in_focus(update, context):
                reset_chat_data(context)
                return ConversationHandler.END

            if not is_group_admin(update, context):
                return not_group_admin(update)

            group_id = context.chat_data.get('group_id', None)
            chat_data: dict = context.chat_data

            group_title = chat_data['group_title']
            token_name = chat_data['tracked_token']
            start_date = chat_data['start_time']
            end_date = chat_data['end_time']
            minimum_buy = chat_data['minimum_buy']
            winner_reward = chat_data['winner_prize']

            # BotService().create_buy_contest(group_id, group_title, token_name, start_date, end_date, minimum_buy, winner_reward)

            template = biggest_buy_competition_alert_template.format(
                group_title=group_title,
                token_name=token_name,
                start_date=start_date,
                end_date=end_date,
                minimum_buy=minimum_buy,
                winner_reward=winner_reward,
                ad="Some special add"
            )

            update.callback_query.answer()
            update.callback_query.edit_message_text(
                text=template, parse_mode=ParseMode.HTML
            )
            context.bot.send_message(
                chat_id=group_id,
                text=template,
                parse_mode=ParseMode.HTML
            )

        self.dispatcher.remove_handler(self.set_confirm_comp_handler)
        reset_chat_data(context)
        return ConversationHandler.END

    def __cancel(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)
        self.__remove_button_handlers()

        if is_private_chat(update):
            if not BotService().is_group_in_focus(update, context):
                reset_chat_data(context)
                return ConversationHandler.END

            if not is_group_admin(update, context):
                return not_group_admin(update)

            if update.message is not None:
                update.message.reply_text(text="<i>❌ Start Biggest Buy session closed. </i>",
                                          parse_mode=ParseMode.HTML)

            else:
                update.callback_query.answer()
                update.callback_query.edit_message_text(
                    text="<i>❌ Start Biggest Buy session closed. </i>",
                    parse_mode=ParseMode.HTML)

        reset_chat_data(context)
        return ConversationHandler.END

    def __goto_start_time(self, update: Update, context: CallbackContext):
        self.dispatcher.add_handler(self.start_time_handler)

        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=set_start_time_template,
            parse_mode=ParseMode.HTML)
        return START_TIME

    def __goto_end_time(self, update: Update, context: CallbackContext):
        self.dispatcher.add_handler(self.end_time_handler)

        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=set_end_time_template,
            parse_mode=ParseMode.HTML)
        return END_TIME

    def __goto_min_buy(self, update: Update, context: CallbackContext):
        self.dispatcher.add_handler(self.min_buy_handler)

        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=set_min_buy_template,
            parse_mode=ParseMode.HTML)
        return MIN_BUY

    def __goto_winner_prize(self, update: Update, context: CallbackContext):
        self.dispatcher.add_handler(self.winner_prize_handler)

        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=set_winner_reward_template,
            parse_mode=ParseMode.HTML)
        return WINNER_PRIZE

    def __goto_start_comp(self, update: Update, context: CallbackContext):
        self.dispatcher.add_handler(self.set_confirm_comp_handler)

        update.callback_query.answer()
        chat_data = context.chat_data

        confirm = InlineKeyboardMarkup([
            [InlineKeyboardButton('Confirm', callback_data='confirm')],
            [InlineKeyboardButton('Cancel', callback_data='cancel')]
        ])

        update.callback_query.edit_message_text(
            text=start_competition_confirmation_template.format(
                token_name=chat_data['tracked_token'],
                start_date=chat_data['start_time'],
                end_date=chat_data['end_time'],
                minimum_buy=chat_data['minimum_buy'],
                winner_reward=chat_data['winner_prize']
            ),
            parse_mode=ParseMode.HTML, reply_markup=confirm)
        return START_TIME

    def __add_handlers(self):
        #  Conversation handlers
        self.dispatcher.add_handler(ConversationHandler(
            entry_points=[CommandHandler('start_buy_contest', self.__start)],
            states={
            },

            fallbacks=[CommandHandler('cancel', self.__cancel), CallbackQueryHandler(
                self.__cancel, pattern='^cancel')],
            conversation_timeout=300,
            name='start_buy_contest',
            allow_reentry=True
        ))

    def __extract_params(self, update: Update, context: CallbackContext):
        self.chattype = update.effective_chat.type
        self.chatid = str(update.effective_chat.id)
        self.chattitle = update.effective_chat.title
        self.chatusername = update.effective_chat.username
        self.group_message_sent_by = update.effective_user.username
        self.bot_name = context.bot.username

    def __reply_template(self, update: Update, context: CallbackContext):
        chat_data = context.chat_data

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton('Set start time', callback_data='set_start_time'),
                InlineKeyboardButton('Set end time', callback_data='set_end_time')],
            [InlineKeyboardButton('Set minimum buy', callback_data='set_min_buy'),
             InlineKeyboardButton('Set winner prize', callback_data='set_winner_prize')],
            [InlineKeyboardButton(
                'Set start competition', callback_data='start_competition')],
            [InlineKeyboardButton(
                'Cancel', callback_data='cancel')]
        ])

        update.message.reply_text(
            text=start_biggest_buy_contest_template.format(
                competition_name=COMPETITION_NAME,
                group_title=chat_data['group_title'],
                token_name=chat_data['tracked_token'],
                start_date=chat_data['start_time'],
                end_date=chat_data['end_time'],
                minimum_buy=chat_data['minimum_buy'],
                winner_reward=chat_data['winner_prize']
            ),
            reply_markup=buttons,
            parse_mode=ParseMode.HTML

        )

    def __create_handlers(self):
        self.set_start_time_hander = CallbackQueryHandler(
            self.__goto_start_time, pattern='set_start_time')

        self.start_time_handler = MessageHandler(Filters.regex(
            '^(2[0-3]|[01]?[0-9])(:[0-5]?[0-9]){2}$'), self.__set_start_time)

        self.set_end_time_handler = CallbackQueryHandler(
            self.__goto_end_time, pattern='set_end_time')

        self.end_time_handler = MessageHandler(Filters.regex(
            '^(2[0-3]|[01]?[0-9])(:[0-5]?[0-9]){2}$'), self.__set_end_time)

        self.set_min_buy_handler = CallbackQueryHandler(
            self.__goto_min_buy, pattern='set_min_buy')

        self.min_buy_handler = MessageHandler(Filters.regex(
            '^\d+$'), self.__set_min_buy)

        self.set_winner_prize_handler = CallbackQueryHandler(
            self.__goto_winner_prize, pattern='set_winner_prize')

        self.winner_prize_handler = MessageHandler(Filters.regex(
            '^\d+$'), self.__set_winner_prize)

        self.set_start_comp_handler = CallbackQueryHandler(
            self.__goto_start_comp, pattern='start_competition')

        self.set_confirm_comp_handler = CallbackQueryHandler(
            self.__start_competition, pattern='confirm')

    def __set_button_handlers(self):
        self.dispatcher.add_handler(self.set_start_time_hander)
        self.dispatcher.add_handler(self.set_end_time_handler)
        self.dispatcher.add_handler(self.set_min_buy_handler)
        self.dispatcher.add_handler(self.set_winner_prize_handler)
        self.dispatcher.add_handler(self.set_start_comp_handler)

    def __remove_button_handlers(self):
        self.dispatcher.remove_handler(self.set_start_time_hander)
        self.dispatcher.remove_handler(self.set_end_time_handler)
        self.dispatcher.remove_handler(self.set_min_buy_handler)
        self.dispatcher.remove_handler(self.set_winner_prize_handler)
        self.dispatcher.remove_handler(self.set_start_comp_handler)
        self.dispatcher.remove_handler(self.set_confirm_comp_handler)

        self.dispatcher.remove_handler(self.start_time_handler)
        self.dispatcher.remove_handler(self.end_time_handler)
        self.dispatcher.remove_handler(self.min_buy_handler)
        self.dispatcher.remove_handler(self.winner_prize_handler)
