
from helpers.flows.public.start_raffle_contest import RaffleContest
from helpers.flows.public.start_buy_contest import BuyContest
from helpers.flows.public.subscription import Subscription
from helpers.flows.public.remove_token import RemoveToken
from helpers.flows.public.add_token import AddToken
from helpers.flows.public.start import StartBot
from helpers.flows.public.general import GeneralHandler
from helpers.bots_imports import *

telegram_bot_token = config('PUBLIC_BOT_API_KEY')
bot = telegram.Bot(token=telegram_bot_token)


updater = Updater(token=telegram_bot_token, use_context=True)
dispatcher = updater.dispatcher


def start_bot():
    updater.bot.set_my_commands(commands=[("help", "Show supported commands"),
                                          ("add_token", "Add the token to be monitored requires token address"),
                                          ("remove_token",
                                           "Remove monitored token"),
                                          ("tracked_tokens",
                                           "List tracked tokens"),
                                          ("start_buy_contest",
                                           "Initiate a biggest buy contest"),
                                          ("raffle_on",
                                           "Start raffle buy contest"),
                                          ("subscribe",
                                           "Subscribe to premium to remove ads"),
                                          ("chains", " Show a list of supported chains"),
                                          ("active_tracking",
                                           "Toggle active buys tracking"),
                                          ("set_buy_icon", "Set buy icon"),
                                          ("set_buy_media",
                                           "Set a gif or image to show with buys"),
                                          ("cancel", "cancel flow"), ])

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
