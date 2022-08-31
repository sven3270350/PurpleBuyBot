from helpers.bots_imports import *

telegram_bot_token = config('ADMIN_BOT_API_KEY')

updater = Updater(token=telegram_bot_token, use_context=True)
dispatcher = updater.dispatcher


# set up the introductory statement for the bot when the /start command is invoked
def start(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text="Hello there. Provide any English word and I will give you a bunch "
                                                   "of information about it.")


# run the start function when the user invokes the /start command
dispatcher.add_handler(CommandHandler("start", start))


updater.start_webhook(listen="0.0.0.0",
                      port=5000,
                      url_path=telegram_bot_token,
                      webhook_url=f"https://{'biggestbuybot'}.herokuapp.com/{telegram_bot_token}")


updater.idle()
