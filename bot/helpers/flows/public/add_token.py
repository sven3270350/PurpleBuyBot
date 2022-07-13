from turtle import update
from eth_utils import is_address
from telegram.ext import CallbackContext, Dispatcher, CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler, Filters
from telegram.utils import helpers
from telegram import ForceReply, Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from services.web3_service import Web3Service
from models import db, SupportedChain, SupportedExchange, SupportedPairs, TrackedToken
from services.bot_service import BotService
from helpers.utils import is_private_chat, is_group_admin
from helpers.templates import add_token_confirmation_template,  not_group_admin_template, add_token_chain_select_template, add_token_dex_select_template, add_token_pair_select_template

DEX, PAIR, ADDRESS, CONFIRM = range(4)


class AddToken:
    def __init__(self, dispatcher: Dispatcher):
        self.dispatcher = dispatcher
        self.__add_handlers()

    def __add_token(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)
        group_id = context.chat_data.get('group_id', None)

        if group_id is None:
            update.message.reply_text(
                text="<i> ❌ No group in focus; use group link first. </i>",
                parse_mode=ParseMode.HTML)
            return ConversationHandler.END

        context.chat_data['group_title'] = context.bot.get_chat(group_id).title
        chat_data: dict = context.chat_data

        if is_private_chat(update):
            if is_group_admin(update, context):
                # list avaialbe chains as buttons
                supported_chains: list[SupportedChain] = BotService(
                ).get_supported_chains()

                if len(supported_chains) == 0:
                    update.message.reply_text(
                        text="<i> ❌ No supported chains found. </i>",
                        parse_mode=ParseMode.HTML)
                    return ConversationHandler.END
                else:
                    buttons = [[InlineKeyboardButton(
                        text=chain.chain_name, callback_data=f'chain_{chain.chain_id}')] for chain in supported_chains]

                    update.message.reply_text(
                        text=add_token_chain_select_template.format(
                            group_title=chat_data.get('group_title', None)
                        ), reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
            else:
                update.message.reply_text(
                    text=not_group_admin_template, parse_mode=ParseMode.HTML)

        return DEX

    def __select_dex(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)
        chat_data: dict = context.chat_data

        message_id = update.callback_query.message.message_id

        if is_private_chat(update):
            if is_group_admin(update, context):
                update.callback_query.answer()
                query = update.callback_query.data
                chain_id = query.split('_')[1]

                chain: SupportedChain = BotService().get_supported_chains(chain_id)
                supported_dexes: list[SupportedExchange] = chain.exchanges

                if (BotService().is_token_set_for_chain(chat_data.get('group_id', None), chain_id)):
                    update.callback_query.message.reply_text(
                        text="❌ Token already set for this chain. Remove the token first")
                    return ConversationHandler.END

                context.chat_data['chain'] = chain

                if len(supported_dexes) == 0:
                    context.bot.edit_message_reply_markup(
                        chain_id=self.chatid, message_id=message_id)
                    update.callback_query.message.reply_text(text="<i> ❌ No supported DEXes found. </i>",
                                                             parse_mode=ParseMode.HTML)
                    return ConversationHandler.END
                else:
                    buttons = [[InlineKeyboardButton(
                        text=dex.exchange_name, callback_data=f'dex_{dex.id}')] for dex in supported_dexes]

                    context.bot.edit_message_text(add_token_dex_select_template.format(
                        group_title=chat_data.get('group_title', None)
                    ), chat_id=self.chatid, message_id=message_id, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
            else:
                update.message.reply_text(text=not_group_admin_template,
                                          parse_mode=ParseMode.HTML)

        return PAIR

    def __select_pair(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)
        chat_data: dict = context.chat_data

        message_id = update.callback_query.message.message_id

        if is_private_chat(update):
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

                    context.bot.edit_message_text(add_token_dex_select_template.format(
                        group_title=chat_data.get('group_title', None)
                    ), chat_id=self.chatid, message_id=message_id, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
            else:
                update.message.reply_text(text=not_group_admin_template,
                                          parse_mode=ParseMode.HTML)

        return ADDRESS

    def __process_pair_select(self,  update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)
        message_id = update.callback_query.message.message_id

        if is_private_chat(update):
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
                update.message.reply_text(text=not_group_admin_template,
                                          parse_mode=ParseMode.HTML)

        return CONFIRM

    def __enter_token_address(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)

        context.bot.send_message(chat_id=self.chatid, text="<i>Enter token address: </i>",
                                 parse_mode=ParseMode.HTML)
        return CONFIRM

    def __confirm_setup(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)
        chat_data: dict = context.chat_data

        group_title = chat_data.get('group_title', None)
        chain: SupportedChain = chat_data.get('chain', None)
        pair: SupportedPairs = chat_data.get('pair', None)
        dex: SupportedExchange = chat_data.get('dex', None)

        token_address = update.message.text

        if token_address and is_address(token_address):
            context.chat_data['token_address'] = token_address

            try:
                token_name, symbol, decimal, pair_address = Web3Service(
                ).get_token_info(token_address, pair.pair_address, dex.factory_address, chain.chain_id)

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
                update.message.reply_text(text=f"<i> ❌ <b>{token_address}</b> is not a valid token. Enter a valid token address </i>",
                                          parse_mode=ParseMode.HTML)
                return CONFIRM
        else:
            update.message.reply_text(text="<i>❌ Invalid token address. Enter a valid address </i>",
                                      parse_mode=ParseMode.HTML)
            return CONFIRM

    def __save_config(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)
        chat_data: dict = context.chat_data

        print(chat_data)

        try:
            # save the token to db
            tracked_tokens = TrackedToken(
                token_address=chat_data['token_address'],
                token_name=chat_data['token_details']['token_name'],
                token_symbol=chat_data['token_details']['symbol'],
                token_decimals=chat_data['token_details']['decimal'],
                pair_address=chat_data['token_details']['pair_address'],
                group_id=chat_data['group_id'],
                chain=[chat_data['chain']]
            )

            db.session.add(tracked_tokens)
            db.session.commit()

            del context.chat_data
            context.chat_data['group_id'] = chat_data['group_id']

            print(context.chat_data)

            context.bot.send_message(chat_id=self.chatid, text=f"<i>✅ Token <b>{chat_data['token_details']['token_name']}</b> added successfully </i>",
                                     parse_mode=ParseMode.HTML)
            return ConversationHandler.END
        except Exception as e:
            print(e)
            context.bot.send_message(chat_id=self.chatid, text=f"<i> ❌ Error adding token, Try again later.</i>",
                                     parse_mode=ParseMode.HTML)
            return ConversationHandler.END

    def __cancel_add_token(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text(text="<i>❌ Add Token Cancelled. </i>",
                                  parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    def __add_handlers(self):
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
                            Filters.text, self.__enter_token_address),

                    ],
                    CONFIRM: [
                        MessageHandler(Filters.text,
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
