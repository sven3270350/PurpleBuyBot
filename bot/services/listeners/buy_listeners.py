from time import sleep
from threading import Thread
from models import  TrackedToken, SupportedPairs, SupportedChain
from services.web3_service import Web3Service
from services.bot_service import BotService
from services.subscriptions_service import SubscriptionService
from telegram import ParseMode
from telegram.ext import CallbackContext
from helpers.templates import regular_buy_template
import asyncio


class BuyListener(Thread):
    def __init__(self, context: CallbackContext):
        Thread.__init__(self)
        self.context = context
        self.is_running = True
        self.is_terminated = False
        
    def run(self):
        while not self.is_running and not self.is_terminated:
            # chech for tokens to track
            tokens_to_track = self.fetch_tokens_to_track()
            if tokens_to_track:
                self.is_running = True

            sleep(10)

        while self.is_running and not self.is_terminated:
            self.run_listener()

    def stop(self):
        self.is_running = False

    def terminate(self):
        self.is_terminated = True

    def fetch_tokens_to_track(self):
        tracked_tokens: list[TrackedToken] = TrackedToken.query.filter_by(
            active_tracking=True).all()

        if not tracked_tokens:
            self.is_running = False

        return tracked_tokens

    async def listen_loop(self, tracked_token: TrackedToken, event_filter, poll_interval=2):
        active_tracking = tracked_token.active_tracking

        while active_tracking:
            for event in event_filter.get_new_entries():
                self.process_event(event['args'], tracked_token)
            await asyncio.sleep(poll_interval)

    def process_event(self, data: dict, tracked_token: TrackedToken):
        amount0_in = data.get('amount0In')
        amount1_out = data.get('amount1Out')
        to = data.get('to')
        token_decimals = tracked_token.token_decimals
        group_id = tracked_token.group_id

        paired_with: SupportedPairs = tracked_token.pair[0]
        chain: SupportedChain = tracked_token.chain[0]

        readable_amount0_in = f"{Web3Service().get_readable_amount(amount0_in, 18)} {paired_with.pair_name}"
        readable_amount1_out = f"{Web3Service().get_readable_amount(amount1_out, token_decimals)} {tracked_token.token_symbol}"

        is_premium_user = SubscriptionService().has_active_subscription(group_id)

        ads = "" if is_premium_user else "<i> Some special ads will be shown here </i>"

        if amount0_in > 0:
            # buy event
            self.context.bot.send_message(
                chat_id=group_id,
                text=regular_buy_template.format(
                    token_name=tracked_token.token_name,
                    amount_in=readable_amount0_in,
                    usd_price=BotService().native_to_usd_by_chain(amount0_in, chain.chain_id),
                    amount_out=readable_amount1_out,
                    chain_name=chain.chain_name,
                    buyer=Web3Service().ellipse_address(to),
                    ad=ads
                ),
                parse_mode=ParseMode.HTML
            )

    def run_listener(self):
        loop = asyncio.new_event_loop()
        tasks = []

        for tracked_token in self.fetch_tokens_to_track():
            chain: SupportedChain = tracked_token.chain[0]
            pair_address = tracked_token.pair_address
            event_filter = Web3Service().get_swap_event_from_pair_address(
                chain.chain_id, pair_address)
            tasks.append(loop.create_task(
                self.listen_loop(tracked_token, event_filter)))

        try:
            loop.run_until_complete(
                asyncio.gather(*tasks)
            )
        finally:
            loop.close()
