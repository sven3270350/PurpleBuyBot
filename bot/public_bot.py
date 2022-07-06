from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from services.bot_service import BotService
from services.biggest_buy_service import BiggestBuyService
from services.bot_service import BotService
from helpers.bots_imports import *
from helpers.templates import start_template, help_template

telegram_bot_token = config('PUBLIC_BOT_API_KEY')
telegram_admin_bot_token = config('ADMIN_BOT_API_KEY')
bot = telegram.Bot(token=telegram_bot_token)
# bot.setWebhook(
#     f"https://{'biggestbuybot'}.herokuapp.com/{telegram_admin_bot_token}")


updater = Updater(token=telegram_bot_token, use_context=True)
dispatcher = updater.dispatcher


def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    chat_title = update.effective_chat.title
    username = update.effective_user.username

    # db
    if (BotService().create_new_bot_user(chat_id, chat_title, username)):
        context.bot.send_message(chat_id=chat_id, text=start_template,
                                 parse_mode=ParseMode.HTML)
    else:
        context.bot.send_message(chat_id=chat_id, text="Error creating new bot user.",
                                 parse_mode=ParseMode.HTML)


def help(update: Update, context: CallbackContext):
    update.message.reply_text(help_template,
                              parse_mode=ParseMode.HTML)


def add_tokens(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=help_template,
                             parse_mode=ParseMode.HTML)


def remove_tokens(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=help_template,
                             parse_mode=ParseMode.HTML)


def start_buy_contest(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=help_template,
                             parse_mode=ParseMode.HTML)


def start_raffle_contest(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=help_template,
                             parse_mode=ParseMode.HTML)


def subscribe(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=help_template,
                             parse_mode=ParseMode.HTML)


def chains(update: Update, context: CallbackContext):
    supported_chains = BotService().get_supported_chains()
    message = '<b>Supported Chains:</b>\n\n'

    if len(supported_chains) == 0:
        message += '<i>No supported chains found.</i>'
    else:
        # loop through the supported chains and add them to the message with numbered list
        for chain in supported_chains:
            message += f'{chain.chain_name}\n'
    update.message.reply_text(message, parse_mode=ParseMode.HTML)


def list_tracked_tokens(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    tracked_tokens = BotService().get_tracked_tokens(chat_id)
    message = "<b>You're Tracking:</b>\n\n"

    if len(tracked_tokens) == 0:
        message += '<i>You currently are not tracking any tokens.</i>\n'
        message += '<i>Use the /add_tokens command to add tokens to your list.</i>'

    else:
        # loop through the supported chains and add them to the message with numbered list
        for token in tracked_tokens:
            message += f'''
            <b>{token.token_symbol} on {token.token_name}</b>
            <i>({token.token_address})</i>
            <i>({token.pair_address})</i>
            '''
    update.message.reply_text(message, parse_mode=ParseMode.HTML)


def get_word_info(update, context):
    # get the word info
    word_info = get_info(update.message.text)

    # If the user provides an invalid English word, return the custom response from get_info() and exit the function
    if word_info.__class__ is str:
        update.message.reply_text(word_info)
        return

    # get the word the user provided
    word = word_info['word']

    # get the origin of the word
    origin = word_info['origin']
    meanings = '\n'

    synonyms = ''
    definition = ''
    example = ''
    antonyms = ''

    # a word may have several meanings. We'll use this counter to track each of the meanings provided from the response
    meaning_counter = 1

    for word_meaning in word_info['meanings']:
        meanings += 'Meaning ' + str(meaning_counter) + ':\n'

        for word_definition in word_meaning['definitions']:
            # extract the each of the definitions of the word
            definition = word_definition['definition']

            # extract each example for the respective definition
            if 'example' in word_definition:
                example = word_definition['example']

            # extract the collection of synonyms for the word based on the definition
            for word_synonym in word_definition['synonyms']:
                synonyms += word_synonym + ', '

            # extract the antonyms of the word based on the definition
            for word_antonym in word_definition['antonyms']:
                antonyms += word_antonym + ', '

        meanings += 'Definition: ' + definition + '\n\n'
        meanings += 'Example: ' + example + '\n\n'
        meanings += 'Synonym: ' + synonyms + '\n\n'
        meanings += 'Antonym: ' + antonyms + '\n\n\n'

        meaning_counter += 1

    # format the data into a string
    message = f"Word: {word}\n\nOrigin: {origin}\n{meanings}"

    update.message.reply_text(message)


# handlers for the commands
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help))
dispatcher.add_handler(CommandHandler("chains", chains))
dispatcher.add_handler(CommandHandler("tracked_tokens", list_tracked_tokens))

# invoke the get_word_info function when the user sends a message
# that is not a command.
# dispatcher.add_handler(MessageHandler(Filters.text, get_word_info))
updater.start_polling()
updater.idle()
