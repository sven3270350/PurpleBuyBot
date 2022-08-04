from datetime import datetime, timedelta
from time import sleep
from threading import Thread
from models import db, Wallet,  SubscriptionType, Subscription
from services.web3_service import Web3Service
from services.subscriptions_service import SubscriptionService
from telegram import Update
from telegram.ext import CallbackContext


class Listener(Thread):
    def __init__(self, update: Update, context: CallbackContext, group_id, chain_id, wallet_id, current_balance, expected_amount):
        Thread.__init__(self)
        self.update = update
        self.context = context
        self.group_id = group_id
        self.chain_id = chain_id
        self.current_balance = current_balance
        self.wallet: Wallet = Wallet.query.filter_by(id=wallet_id).first()
        self.expected_amount = expected_amount
        self.is_running = True
        self.timeout = 60 * 5  # 5 minutes
        self.start_time = datetime.now()

    def run(self):
        while self.is_running:
            self.check_for_payment()
            sleep(5)

    def stop(self):
        self.is_running = False

    def check_for_payment(self):

        if self.wallet.wallet_address:
            balance = Web3Service().get_wallet_balance(
                self.chain_id, self.wallet.wallet_address)

            if (balance - self.current_balance) >= self.expected_amount:
                self.stop()
                self.process_payment()

        if (datetime.now() - self.start_time).total_seconds() > self.timeout:
            self.stop()
            self.context.bot.send_message(
                chat_id=self.update.effective_chat.id, text="❌ Payment not received. Use /subscribe to check payment.")

    def process_payment(self):
        pending_subscription: Subscription = SubscriptionService(
        ).get_group_pending_subscription(self.group_id)

        subscription_type: SubscriptionType = SubscriptionService().get_subscription_plan_by_id(
            pending_subscription.subscription_type_id)

        start_date = datetime.now()
        end_date = (start_date + timedelta(years=200)) if subscription_type.subscription_type == 'Lifetime' else (
            start_date + timedelta(weeks=pending_subscription.number_of_countable_subscriptions))

        if pending_subscription:
            pending_subscription.start_date = start_date
            pending_subscription.end_date = end_date
            pending_subscription.tx_hash = None
            pending_subscription.status = 'paid',

            db.session.add(pending_subscription)
            db.session.commit()
            self.stop()

            Web3Service().transfer_balance_to_admin(self.chain_id, self.wallet.id)

            chat_id = self.update.effective_chat.id
            self.context.bot.send_message(
                chat_id=chat_id, text=f"✅ Payment received. Subscription started on {start_date} and will expire on {end_date}")
