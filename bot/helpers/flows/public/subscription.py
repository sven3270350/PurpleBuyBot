from datetime import datetime, timedelta
import web3
from web3.types import TxData, TxReceipt
from telegram.ext import (
    CallbackContext, Dispatcher, ConversationHandler,
    CommandHandler, CallbackQueryHandler, MessageHandler, Filters)
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from services.listener import Listener
from services.web3_service import Web3Service
from services.bot_service import BotService
from services.subscriptions_service import SubscriptionService
from helpers.utils import (
    is_private_chat, is_group_admin,
    send_typing_action, reset_chat_data, not_group_admin, set_commands, response_for_group)
from helpers.templates import (
    no_active_subscription_template, active_subscription_template,
    weekly_subscription_template, subscription_confirmation_template,
    check_payment_template, payment_status_template, has_pending_subscription_template,
    final_subscription_review_template)
from models import (
    db, SupportedChain, Subscription as SubscriptionModel, SubscriptionType, Wallet)

SELECT, CONFIRM, CHECK, CONFIRM_PAYMENT, CHECK_PAYMENT_FROM_CHAIN = range(5)

cancel_button = [
    InlineKeyboardButton(
        "Cancel",
        callback_data=f"cancel")
]


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

            set_commands(context, True)

            group_id = context.chat_data.get('group_id', None)
            context.chat_data['group_title'] = context.bot.get_chat(
                group_id).title
            chat_data: dict = context.chat_data

            if not is_group_admin(update, context):
                return not_group_admin(update)

            check_payment_button = InlineKeyboardButton(
                "Check payment",
                callback_data=f"check_payment")

            # check for pending subscription
            pending_subscription: SubscriptionModel = SubscriptionService(
            ).get_group_pending_subscription(group_id)

            chain: SupportedChain = BotService().get_supported_chains(
                pending_subscription.payment_chain_id) if pending_subscription else None

            if pending_subscription:
                subscription_type: SubscriptionType = SubscriptionService().get_subscription_plan_by_id(
                    pending_subscription.subscription_type_id)
                wallet: Wallet = BotService().get_group_wallet(group_id)

                expected_amount = web3.Web3.fromWei(
                    pending_subscription.expected_amount_in_native_wei, 'ether')

                update.message.reply_text(
                    text=has_pending_subscription_template.format(
                        total_cost=f'{expected_amount} {chain.native_symbol}',
                        payment_address=wallet.wallet_address,
                        subscription=subscription_type.subscription_type,
                        chain_name=chain.chain_name),
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup([
                        [check_payment_button]
                    ]))

                return SELECT

            # show currect subscription plan
            active_subscriptions: list[SubscriptionModel] = SubscriptionService(
            ).get_active_active_subscription_by_group_id(group_id)

            if len(active_subscriptions) > 0:
                active_subscription: SubscriptionModel = active_subscriptions[0]

                # show current subscription plan
                extra = active_subscription.total or (
                    'For Life' if active_subscription.for_life else False)

                update.message.reply_text(
                    text=active_subscription_template.format(
                        group_title=chat_data[
                            'group_title'],
                        package=f'{active_subscription.subscription_type} {f"({extra})" if extra else ""}',
                        start_date=active_subscription.start_date,
                        end_date=active_subscription.end_date
                    ),
                    parse_mode=ParseMode.HTML)
                reset_chat_data(context)
                return ConversationHandler.END
            else:

                # show sumbscription plans
                plans: list[SubscriptionType] = SubscriptionService(
                ).get_subscription_plans()

                keyboard = []
                for plan in plans:
                    keyboard.append(
                        [InlineKeyboardButton(
                            f"{plan.subscription_type} (${plan.usd_price})",
                            callback_data=f"subscription_type:{plan.id}")])

                keyboard.append([check_payment_button])

                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text(
                    text=no_active_subscription_template.format(
                        group_title=chat_data['group_title']),
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML)

                return SELECT
        else:
            if is_group_admin(update, context):
                response_for_group(self, update)

        reset_chat_data(context)
        return ConversationHandler.END

    @send_typing_action
    def __select_subscription(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)
        message_id = update.callback_query.message.message_id

        if not is_group_admin(update, context):
            return not_group_admin(update)

        update.callback_query.answer()
        query = update.callback_query.data
        subscription_type_id = query.split(':')[1]

        subscription_details: SubscriptionType = SubscriptionService(
        ).get_subscription_plan_by_id(subscription_type_id)

        context.chat_data['subscription_type'] = subscription_details

        if subscription_details.subscription_type == 'Weekly':
            # is weekly subscription
            button = InlineKeyboardButton(
                "Proceed",
                callback_data=f"proceed_from:{subscription_type_id}")
            keyboard = [[button], cancel_button]

            context.chat_data['select_number_of_weeks'] = MessageHandler(
                Filters.regex('^\d+$'), self.__weekly_subscription)
            self.dispatcher.add_handler(
                context.chat_data['select_number_of_weeks'])

            context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=message_id,
                text=weekly_subscription_template,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard))

            return CONFIRM

        return self.__send_confirmation_message(update, context)

    def __select_amount(self, update: Update, context: CallbackContext) -> int:
        return self.__send_confirmation_message(update, context)

    @send_typing_action
    def __weekly_subscription(self,  update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)
        chat_data = context.chat_data
        self.dispatcher.remove_handler(
            chat_data['select_number_of_weeks'])

        return self.__send_confirmation_message(update, context)

    @send_typing_action
    def __check_payment_status(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)
        update.callback_query.answer()

        # select chain to check payment status
        supported_chains: list[SupportedChain] = BotService(
        ).get_supported_chains()

        keyboard = []
        if len(supported_chains) > 0:
            for chain in supported_chains:
                keyboard.append(
                    [InlineKeyboardButton(
                        f"{chain.chain_name}",
                        callback_data=f"confirm_payment:{chain.chain_id}")])

            keyboard.append(cancel_button)
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.callback_query.edit_message_text(
                text=check_payment_template,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML)

            return CONFIRM_PAYMENT

        update.callback_query.edit_message_text(
            text="No supported chains found",
            parse_mode=ParseMode.HTML)

        reset_chat_data(context)
        return ConversationHandler.END

    @send_typing_action
    def __confirm_payment(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)

        update.callback_query.answer()
        query = update.callback_query.data
        chain_id = query.split(':')[1]

        chain: SupportedChain = BotService().get_supported_chains(chain_id)

        context.chat_data['chain'] = chain

        if not chain:
            update.callback_query.edit_message_text(
                text="No supported chains found",
                parse_mode=ParseMode.HTML)

            reset_chat_data(context)
            return ConversationHandler.END

        update.callback_query.edit_message_text(
            text=payment_status_template.format(
                chain_name=chain.chain_name,
                status_message='Please enter transaction hash',
                transaction_hash='[transaction_hash]'
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([cancel_button])
        )

        return CONFIRM_PAYMENT

    @send_typing_action
    def __check_payment_hash(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)
        chat_data = context.chat_data
        group_id = chat_data['group_id']
        transaction_hash = update.message.text
        chain: SupportedChain = chat_data['chain']
        pending_subscription: SubscriptionModel = SubscriptionService(
        ).get_group_pending_subscription(group_id)

        if not pending_subscription:
            update.message.reply_text(
                text=payment_status_template.format(
                    chain_name=chain.chain_name,
                    status_message='You have no pending subscription',
                    transaction_hash=transaction_hash
                ),
                parse_mode=ParseMode.HTML
            )

            reset_chat_data(context)
            return ConversationHandler.END

        subscription_type: SubscriptionType = SubscriptionService().get_subscription_plan_by_id(
            pending_subscription.subscription_type_id)

        if transaction_hash and BotService().is_tx_hash_unique(transaction_hash):

            if not chain:
                update.message.reply_text(
                    text="No supported chains found",
                    parse_mode=ParseMode.HTML)

                reset_chat_data(context)
                return ConversationHandler.END

            payment_status: TxData = Web3Service().get_transaction_receipt(
                chain.chain_id, transaction_hash)

            group_wallet: Wallet = BotService().get_group_wallet(
                chat_data['group_id'])

            if payment_status.blockNumber is None:
                update.message.reply_text(
                    text=payment_status_template.format(
                        chain_name=chain.chain_name,
                        status_message='Transaction is pending',
                        transaction_hash=transaction_hash
                    ),
                    parse_mode=ParseMode.HTML
                )
                reset_chat_data(context)
                return ConversationHandler.END

            block_timestampe: datetime = Web3Service(
            ).get_block_timestamp(chain.chain_id, payment_status.blockNumber)

            # Check if transaction is valid
            same_address = payment_status.to.lower() == group_wallet.wallet_address.lower()
            same_amount = payment_status.value == pending_subscription.expected_amount_in_native_wei
            end_date = (block_timestampe + timedelta(years=200)) if subscription_type.subscription_type == 'Lifetime' else (
                block_timestampe + timedelta(weeks=pending_subscription.number_of_countable_subscriptions))

            if same_address and same_amount:
                try:
                    # update subscription status
                    pending_subscription.tx_hash = transaction_hash
                    pending_subscription.start_date = block_timestampe
                    pending_subscription.end_date = end_date
                    pending_subscription.status = 'paid',
                    db.session.add(pending_subscription)
                    db.session.commit()

                    update.message.reply_text(
                        text=payment_status_template.format(
                            chain_name=chain.chain_name,
                            status_message='Transaction confirmed',
                            transaction_hash=transaction_hash
                        ),
                        parse_mode=ParseMode.HTML
                    )
                except Exception as e:
                    db.session.rollback()
                    update.message.reply_text(
                        text=payment_status_template.format(
                            chain_name=chain.chain_name,
                            status_message='Error occured, try again or contact support',
                            transaction_hash=transaction_hash
                        ),
                        parse_mode=ParseMode.HTML
                    )

            reset_chat_data(context)
            return ConversationHandler.END

        update.message.reply_text(
            text=payment_status_template.format(
                chain_name=chain.chain_name,
                status_message='Transaction hash is not valid/already used',
                transaction_hash=transaction_hash
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([cancel_button])
        )

        return CONFIRM_PAYMENT

    def __confirm_subscripton(self, update: Update, context: CallbackContext):
        self.__extract_params(update, context)
        message_id = update.callback_query.message.message_id
        chat_data: dict = context.chat_data

        if not is_group_admin(update, context):
            return not_group_admin(update)

        update.callback_query.answer()
        subscription_type: SubscriptionType = context.chat_data['subscription_type']
        wallet: Wallet = BotService().get_group_wallet(chat_data['group_id'])
        subscription_count = int(chat_data['subscription_count'])
        chain_id = context.chat_data['chain'].chain_id

        if not subscription_type:
            update.callback_query.edit_message_text(
                text="No subscription type found",
                parse_mode=ParseMode.HTML)

            reset_chat_data(context)
            return ConversationHandler.END

        # Create a new subscription
        try:
            number_of_subscription = subscription_count if subscription_count else 1

            expected_amount = BotService().usd_to_native_price_by_chain(
                subscription_type.usd_price, number_of_subscription,  chain_id)

            group_id = context.chat_data['group_id']
            subscription = SubscriptionModel(
                group_id=group_id,
                subscription_type_id=subscription_type.id,
                payment_chain_id=chain_id,
                wallet_id=wallet.id,
                status='pending',
                number_of_countable_subscriptions=(
                    subscription_count if subscription_count else 1),
                is_life_time_subscription=True if subscription_type.subscription_type == 'Lifetime' else False,
                expected_amount_in_native_wei=expected_amount)

            db.session.add(subscription)
            db.session.commit()

            current_balance = Web3Service().get_wallet_balance(
                chain_id, wallet.wallet_address)
            # start a listener for the transaction
            self.__start_listener_for_payment(
                update, context, group_id, chain_id, wallet.id, current_balance, expected_amount)

            context.bot.edit_message_reply_markup(
                chat_id=update.callback_query.message.chat_id,
                message_id=message_id,
                reply_markup=InlineKeyboardMarkup([[]]))

            context.bot.send_message(
                text=f"<i>✅ Subscription Recorded! It will be activated after payment is confirmed</i>",
                chat_id=self.chatid,
                parse_mode=ParseMode.HTML
            )

            reset_chat_data(context)
            return ConversationHandler.END

        except Exception as e:
            db.session.rollback()
            print(e)
            update.callback_query.edit_message_text(
                text="Error creating subscription",
                parse_mode=ParseMode.HTML)

            reset_chat_data(context)
            return ConversationHandler.END

    @ send_typing_action
    def __cancel(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)

        if update.message is not None:
            update.message.reply_text(text="<i>❌ Subscription session closed. </i>",
                                      parse_mode=ParseMode.HTML)

        else:
            update.callback_query.answer()
            update.callback_query.edit_message_text(
                text="<i>❌ Subscription session closed. </i>",
                parse_mode=ParseMode.HTML)

        reset_chat_data(context)
        return ConversationHandler.END

    def __send_confirmation_message(self, update: Update, context: CallbackContext):
        self.__extract_params(update, context)
        chat_data = context.chat_data

        subscription: SubscriptionType = context.chat_data['subscription_type']
        supported_chains: list[SupportedChain] = BotService(
        ).get_supported_chains()

        keyboard = []
        if len(supported_chains) > 0:
            for chain in supported_chains:
                keyboard.append(
                    [InlineKeyboardButton(
                        f"{chain.chain_name}",
                        callback_data=f"selected_payment_chain:{chain.chain_id}")])

            keyboard.append(cancel_button)
            reply_markup = InlineKeyboardMarkup(keyboard)

        context.chat_data['subscription_count'] = 1
        if update.message is not None:
            message = update.message.text
            context.chat_data['subscription_count'] = message
            update.message.reply_text(
                text=subscription_confirmation_template.format(
                    group_title=chat_data['group_title'],
                    package=f'{subscription.subscription_type} {f"({message})" if message else ""}',
                    total_cost=f'${subscription.usd_price * (int(message) if message else 1)}'),
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup)
        else:
            update.callback_query.answer()
            update.callback_query.message.edit_text(
                text=subscription_confirmation_template.format(
                    group_title=chat_data['group_title'],
                    package=f'{subscription.subscription_type}',
                    total_cost=f'${subscription.usd_price }'),
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup)

        return CONFIRM

    @send_typing_action
    def __final_review(self, update: Update, context: CallbackContext) -> int:
        self.__extract_params(update, context)
        update.callback_query.answer()

        chat_data = context.chat_data

        query = update.callback_query.data
        chain_id = query.split(':')[1]

        chain: SupportedChain = BotService().get_supported_chains(chain_id)
        subscription: SubscriptionType = chat_data['subscription_type']
        count = chat_data['subscription_count']
        wallet: Wallet = BotService().get_group_wallet(chat_data['group_id'])

        if not chain:
            update.callback_query.edit_message_text(
                text="<i>❌ Invalid payment chain</i>",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([cancel_button])
            )

            return CONFIRM_PAYMENT

        context.chat_data['chain'] = chain
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "Confirm",
                callback_data=f"confirm_subscription:{subscription.id}")
        ]])

        update.callback_query.message.edit_text(
            text=final_subscription_review_template.format(
                group_title=chat_data['group_title'],
                package=f'{subscription.subscription_type} {f"({count})" if count else ""}',
                total_cost=f'{web3.Web3.fromWei(BotService().usd_to_native_price_by_chain(subscription.usd_price, count, chain_id), "ether")} {chain.native_symbol}',
                chain_name=chain.chain_name,
                wallet=wallet.wallet_address),
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup)

        return CONFIRM

    def __add_handlers(self):
        self.dispatcher.add_handler(ConversationHandler(
            entry_points=[CommandHandler('subscribe', self.__subscribe)],
            states={
                SELECT: [CallbackQueryHandler(self.__select_subscription, pattern='^subscription_type:\d+'),
                         CallbackQueryHandler(self.__check_payment_status, pattern='check_payment')],
                CONFIRM: [CallbackQueryHandler(
                    self.__confirm_subscripton, pattern='^confirm_subscription:\d+'),
                    CallbackQueryHandler(
                        self.__select_amount, pattern='^proceed_from:\d+'),
                    CallbackQueryHandler(self.__final_review, pattern='^selected_payment_chain:\d+')],
                CONFIRM_PAYMENT: [CallbackQueryHandler(self.__confirm_payment, pattern='^confirm_payment:\d+'),
                                  MessageHandler(Filters.regex('^0x[a-zA-Z0-9]{64}$'), self.__check_payment_hash)],

            },
            fallbacks=[CommandHandler('cancel', self.__cancel), CallbackQueryHandler(
                self.__cancel, pattern='^cancel')],
            conversation_timeout=300,
            name='subscription'
        ))

    def __extract_params(self, update: Update, context: CallbackContext):
        self.chattype = update.effective_chat.type
        self.chatid = str(update.effective_chat.id)
        self.chattitle = update.effective_chat.title
        self.chatusername = update.effective_chat.username
        self.group_message_sent_by = update.effective_user.username
        self.bot_name = context.bot.username

    def __start_listener_for_payment(self, update, context, group_id, chain_id, wallet_id, current_balance, expected_amount):
        listener = Listener(update, context, group_id, chain_id, wallet_id,
                            current_balance, expected_amount)
        listener.start()
        return listener
