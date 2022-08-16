from eth_utils import is_address
from telegram.ext import CallbackContext, Dispatcher, CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler, Filters
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from services.web3_service import Web3Service
from models import db, SupportedChain, SupportedExchange, SupportedPairs, TrackedToken
from services.bot_service import BotService
from helpers.utils import is_private_chat, is_group_admin, send_typing_action, reset_chat_data, not_group_admin
from helpers.templates import add_token_confirmation_template, add_token_chain_select_template, add_token_dex_select_template, add_token_pair_select_template

DEX, PAIR, ADDRESS, CONFIRM = range(4)


class AddToken:
    def __init__(self, dispatcher: Dispatcher):
        self.dispatcher = dispatcher
        self.__add_handlers()

    @send_typing_action
    def __add_token(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)

        if is_private_chat(update):
            if not BotService().is_group_in_focus(update, context):
                reset_chat_data(context)
                return ConversationHandler.END

            group_id = context.chat_data.get('group_id', None)

            context.chat_data['group_title'] = context.bot.get_chat(
                group_id).title
            chat_data: dict = context.chat_data

            if is_group_admin(update, context):
                # list avaialbe chains as buttons
                supported_chains: list[SupportedChain] = BotService(
                ).get_supported_chains()

                if len(supported_chains) == 0:
                    update.message.reply_text(
                        text="<i> ❌ No supported chains found. </i>",
                        parse_mode=ParseMode.HTML)

                    reset_chat_data(context)
                    return ConversationHandler.END
                else:
                    buttons = [[InlineKeyboardButton(
                        text=chain.chain_name, callback_data=f'chain_{chain.chain_id}')] for chain in supported_chains]

                    update.message.reply_text(
                        text=add_token_chain_select_template.format(
                            group_title=chat_data.get('group_title', None)
                        ), reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
            else:
                return not_group_admin(update, context)

            return DEX

        return ConversationHandler.END

    @send_typing_action
    def __select_dex(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)
        chat_data: dict = context.chat_data

        message_id = update.callback_query.message.message_id

        if is_group_admin(update, context):
            update.callback_query.answer()
            query = update.callback_query.data
            chain_id = query.split('_')[1]

            chain: SupportedChain = BotService().get_supported_chains(chain_id)
            supported_dexes: list[SupportedExchange] = chain.exchanges

            if (BotService().is_token_set_for_chain(chat_data.get('group_id', None), chain_id)):
                update.callback_query.message.reply_text(
                    text="❌ Token already set for this chain. Remove the token first")

                reset_chat_data(context)
                return ConversationHandler.END

            context.chat_data['chain'] = chain

            if len(supported_dexes) == 0:
                context.bot.edit_message_reply_markup(
                    chain_id=self.chatid, message_id=message_id)
                update.callback_query.message.reply_text(text="<i> ❌ No supported DEXes found. </i>",
                                                         parse_mode=ParseMode.HTML)

                reset_chat_data(context)
                return ConversationHandler.END
            else:
                buttons = [[InlineKeyboardButton(
                    text=dex.exchange_name, callback_data=f'dex_{dex.id}')] for dex in supported_dexes]

                context.bot.edit_message_text(add_token_dex_select_template.format(
                    group_title=chat_data.get('group_title', None)
                ), chat_id=self.chatid, message_id=message_id, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
        else:
            return not_group_admin(update, context)

        return PAIR

    @send_typing_action
    def __select_pair(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)
        chat_data: dict = context.chat_data

        message_id = update.callback_query.message.message_id

        if is_group_admin(update, context):
            update.callback_query.answer()
            query = update.callback_query.data
            dex_id = query.split('_')[1]

            chain: SupportedChain = context.chat_data['chain']
            selected_dex: SupportedExchange = BotService().get_supported_dex_by_id(dex_id)
            supported_pairs: list[SupportedPairs] = chain.pairs

            context.chat_data['dex'] = selected_dex

            if len(supported_pairs) == 0:
                update.callback_query.answer(text="<i> ❌ No supported Pairs found. </i>",
                                             parse_mode=ParseMode.HTML)
                return ConversationHandler.END
            else:
                buttons = [[InlineKeyboardButton(
                    text=pair.pair_name, callback_data=f'pair_{pair.id}')] for pair in supported_pairs]

                context.bot.edit_message_text(add_token_pair_select_template.format(
                    group_title=chat_data.get('group_title', None)
                ), chat_id=self.chatid, message_id=message_id, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
        else:
            return not_group_admin(update, context)

        return ADDRESS

    @send_typing_action
    def __process_pair_select(self,  update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)
        message_id = update.callback_query.message.message_id

        if is_group_admin(update, context):
            update.callback_query.answer()
            query = update.callback_query.data
            pair_id = query.split('_')[1]

            selected_pair: SupportedPairs = BotService().get_supported_pair_by_id(pair_id)

            context.chat_data['pair'] = selected_pair

            context.bot.edit_message_text("<i>Enter token address: </i>",
                                          chat_id=self.chatid, message_id=message_id, parse_mode=ParseMode.HTML)

            return CONFIRM
        else:
            return not_group_admin(update, context)

    @send_typing_action
    def __enter_token_address(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)

        if is_group_admin(update, context):

            context.bot.send_message(chat_id=self.chatid, text="<i>Enter token address: </i>",
                                     parse_mode=ParseMode.HTML)
        else:
            return not_group_admin(update, context)
        return CONFIRM

    @send_typing_action
    def __confirm_setup(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)
        chat_data: dict = context.chat_data

        group_title = chat_data.get('group_title', None)
        chain: SupportedChain = chat_data.get('chain', None)
        pair: SupportedPairs = chat_data.get('pair', None)
        dex: SupportedExchange = chat_data.get('dex', None)

        token_address = update.message.text

        if is_group_admin(update, context):

            if token_address and is_address(token_address):
                context.chat_data['token_address'] = token_address

                try:
                    token_name, symbol, decimal, pair_address, is_valid_pair = Web3Service(
                    ).get_token_info(token_address, pair.pair_address, dex.factory_address, chain.chain_id)

                    if not is_valid_pair:
                        update.message.reply_text(text="<i> ❌ The pair selected has no liquidity. </i>",
                                                  parse_mode=ParseMode.HTML)

                        reset_chat_data(context)
                        return ConversationHandler.END

                    chat_data['token_details'] = {
                        'token_name': token_name,
                        'symbol': symbol,
                        'decimal': decimal,
                        'pair_address': pair_address
                    }

                    button = [[InlineKeyboardButton(
                        text='Proceed', callback_data="confirm")]]

                    update.message.reply_text(text=add_token_confirmation_template.format(
                        group_title=group_title, chain=chain.chain_name, dex=dex.exchange_name, pair=f'{symbol}/{pair.pair_name}', token_address=token_name
                    ),
                        parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(button))
                    return CONFIRM
                except Exception as e:
                    print(e)
                    update.message.reply_text(text=f"<i> ❌ <b>{token_address}</b> is not a valid token. Enter a valid token address </i>",
                                              parse_mode=ParseMode.HTML)
                    return CONFIRM
            else:
                update.message.reply_text(text="<i>❌ Invalid token address. Enter a valid address </i>",
                                          parse_mode=ParseMode.HTML)
                return CONFIRM
        else:
            return not_group_admin(update, context)

    @send_typing_action
    def __save_config(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)
        chat_data: dict = context.chat_data

        if is_group_admin(update, context):

            try:
                # save the token to db
                tracked_tokens = TrackedToken(
                    token_address=chat_data['token_address'],
                    token_name=chat_data['token_details']['token_name'],
                    token_symbol=chat_data['token_details']['symbol'],
                    token_decimals=chat_data['token_details']['decimal'],
                    pair_address=chat_data['token_details']['pair_address'],
                    group_id=chat_data['group_id'],
                    chain=[chat_data['chain']],
                    pair=[chat_data['pair']],
                    dex=[chat_data['dex']]
                )

                db.session.add(tracked_tokens)
                db.session.commit()

                context.bot.send_message(chat_id=self.chatid, text=f"<i>✅ Token <b>{chat_data['token_details']['token_name']}</b> added successfully </i>",
                                         parse_mode=ParseMode.HTML)

                reset_chat_data(context)
                return ConversationHandler.END
            except Exception as e:
                print(e)
                context.bot.send_message(chat_id=self.chatid, text=f"<i> ❌ Error adding token, Try again later.</i>",
                                         parse_mode=ParseMode.HTML)

                reset_chat_data(context)
                return ConversationHandler.END
        else:
            return not_group_admin(update, context)

    @send_typing_action
    def __active_tracking(self, update: Update, context: CallbackContext):
        self.__extract_params(update, context)
        if is_private_chat(update):
            if not BotService().is_group_in_focus(update, context):
                reset_chat_data(context)
                return ConversationHandler.END

            group_id = context.chat_data.get('group_id', None)
            if not is_group_admin(update, context):
                return not_group_admin(update, context)

            active_tracked_token: TrackedToken = TrackedToken.query.filter_by(
                group_id=group_id, active_tracking=True).first()

            if active_tracked_token:
                disable_button = [[InlineKeyboardButton(
                    text='Disable Tracking', callback_data="disable")]]

                self.__add_disable_tracking_handler()

                update.message.reply_text(
                    text=f"<i> Buys for <b>{active_tracked_token.token_name}</b> is being tracked </i>",
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup(disable_button)
                )
            else:
                enable_button = [[InlineKeyboardButton(
                    text='Enable Tracking', callback_data="enable")]]

                self.__add_enbale_tracking_handler()

                update.message.reply_text(
                    text=f"<i> You haven't enabled buy tracking </i>",
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup(enable_button)
                )

    @send_typing_action
    def __cancel_add_token(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text(text="<i>❌ Add Token Cancelled. </i>",
                                  parse_mode=ParseMode.HTML)

        reset_chat_data(context)
        return ConversationHandler.END

    def __add_handlers(self):
        self.dispatcher.add_handler(CommandHandler(
            'active_tracking', self.__active_tracking))
        self.dispatcher.add_handler(
            ConversationHandler(
                entry_points=[
                    CommandHandler('add_token', self.__add_token)
                ],
                states={
                    DEX: [
                        CallbackQueryHandler(
                            self.__select_dex, pattern='^chain_.*'),
                    ],
                    PAIR: [
                        CallbackQueryHandler(
                            self.__select_pair, pattern='^dex_.*'),
                    ],
                    ADDRESS: [
                        CallbackQueryHandler(
                            self.__process_pair_select, pattern='^pair_.*'),
                        MessageHandler(
                            Filters.regex('^0x\w{40}$'), self.__enter_token_address),

                    ],
                    CONFIRM: [
                        MessageHandler(Filters.regex('^0x\w{40}$'),
                                       self.__confirm_setup),
                        CallbackQueryHandler(
                            self.__save_config, pattern='confirm'),
                    ]
                },
                fallbacks=[
                    CommandHandler('cancel', self.__cancel_add_token)
                ],
                conversation_timeout=300,
                name='add_token',


            )
        )

    def __extract_params(self, update: Update, context: CallbackContext):
        self.chattype = update.effective_chat.type
        self.chatid = str(update.effective_chat.id)
        self.chattitle = update.effective_chat.title
        self.chatusername = update.effective_chat.username
        self.group_message_sent_by = update.effective_user.username
        self.bot_name = context.bot.username

    def __enable_tracking(self, update: Update, context: CallbackContext):
        group_id = context.chat_data.get('group_id', None)
        group_tracked_token: list[TrackedToken] = TrackedToken.query.filter_by(
            group_id=group_id).all()

        if group_tracked_token:
            for token in group_tracked_token:
                token.active_tracking = True
                db.session.commit()

            update.callback_query.answer()
            update.callback_query.edit_message_text(text="<i>✅ Tracking enabled successfully </i>",
                                                    parse_mode=ParseMode.HTML)
        self.__remove_enbale_tracking_handler()

    def __disable_tracking(self, update: Update, context: CallbackContext):
        group_id = context.chat_data.get('group_id', None)
        group_tracked_token: list[TrackedToken] = TrackedToken.query.filter_by(
            group_id=group_id, active_tracking=True).all()

        if group_tracked_token:
            for token in group_tracked_token:
                token.active_tracking = False
                db.session.commit()

            update.callback_query.answer()
            update.callback_query.edit_message_text(text="<i>✅ Tracking disabled successfully </i>",
                                                    parse_mode=ParseMode.HTML)

        self.__remove_disable_tracking_handler()

    def __add_enbale_tracking_handler(self):
        self.enable_tracking_handler = CallbackQueryHandler(
            self.__enable_tracking, pattern='^enable$')
        self.dispatcher.add_handler(self.enable_tracking_handler)

    def __add_disable_tracking_handler(self):
        self.disable_tracking_handler = CallbackQueryHandler(
            self.__disable_tracking, pattern='^disable$')
        self.dispatcher.add_handler(self.disable_tracking_handler)

    def __remove_enbale_tracking_handler(self):
        self.dispatcher.remove_handler(self.enable_tracking_handler)

    def __remove_disable_tracking_handler(self):
        self.dispatcher.remove_handler(self.disable_tracking_handler)
