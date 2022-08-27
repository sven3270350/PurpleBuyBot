
from services.listeners.buy_listeners import buy_listener
from helpers.flows.public.start_raffle_contest import RaffleContest
from helpers.flows.public.start_buy_contest import BuyContest
from helpers.flows.public.subscription import Subscription
from helpers.flows.public.remove_token import RemoveToken
from helpers.flows.public.add_token import AddToken
from helpers.flows.public.start import StartBot
from helpers.flows.public.general import GeneralHandler
from helpers.bots_imports import *

telegram_bot_token = config('PUBLIC_BOT_API_KEY')
telegram_admin_bot_token = config('ADMIN_BOT_API_KEY')
bot = telegram.Bot(token=telegram_bot_token)


updater = Updater(token=telegram_bot_token, use_context=True)
dispatcher = updater.dispatcher


def start_bot():
    updater.start_webhook(listen="0.0.0.0",
                          port=int(os.environ.get('PORT', 5000)),
                          url_path=telegram_bot_token,
                          webhook_url=f"https://{'biggestbuybot'}.herokuapp.com/{telegram_bot_token}")
    updater.idle()
    # updater.start_polling()


def main():
    # call handlers for start commands
    StartBot(dispatcher)
    AddToken(dispatcher)
    RemoveToken(dispatcher)
    Subscription(dispatcher)
    GeneralHandler(dispatcher)
    BuyContest(dispatcher)
    RaffleContest(dispatcher)
    start_bot()


if __name__ == '__main__':
    main()
