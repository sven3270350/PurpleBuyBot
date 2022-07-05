import os
import telegram
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler
from App import get_info
from decouple import config