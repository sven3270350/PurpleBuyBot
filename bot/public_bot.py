from helpers.flows.public.start_buy_contest import BuyContest
from helpers.flows.public.subscription import Subscription
from helpers.flows.public.remove_token import RemoveToken
from helpers.flows.public.add_token import AddToken
from helpers.flows.public.start import StartBot
from helpers.flows.public.general import GeneralHandler
import html
import json
import logging
import traceback
from helpers.bots_imports import *
from telegram import Update
from telegram import ParseMode

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

DEVELOPER_CHAT_ID = '567495946'

telegram_bot_token = config('PUBLIC_BOT_API_KEY')
bot = telegram.Bot(token=telegram_bot_token)


updater = Updater(token=telegram_bot_token, use_context=True)
dispatcher = updater.dispatcher


def error_handler(update: object, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:",
                 exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    context.bot.send_message(
        chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
    )


def start_bot():
    updater.bot.set_my_commands(commands=[("help", "Show supported commands"),
                                          ("add_token", "Add the token to be monitored requires token address"),
                                          ("remove_token",
                                           "Remove monitored token"),
                                          ("tracked_tokens",
                                           "List tracked tokens"),
                                          ("start_buy_contest",
                                           "Start a biggest buy contest"),
                                          ("raffle_on",
                                           "Start raffle buy contest"),
                                          ("start_lastbuy_contest",
                                           "Start a last buy contest"),
                                          ("active_contest",
                                           "Show active contest and cancel if needed"),
                                          ("subscribe",
                                           "Subscribe to premium to remove ads"),
                                          ("chains", " Show a list of supported chains"),
                                          ("active_tracking",
                                           "Toggle active buy tracking"),
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
    dispatcher.add_error_handler(error_handler)
    start_bot()


if __name__ == '__main__':
    main()
