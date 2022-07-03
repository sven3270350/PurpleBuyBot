release: cd app && flask db migrate && flask db upgrade
bot1: python app/public_bot.py $PORT
bot2: python app/admin_bot.py $PORT
web: gurnicon app:app