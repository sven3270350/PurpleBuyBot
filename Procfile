release: export FLASK_APP=bot:app && flask db upgrade
bot1: python app/bots/public_bot.py $PORT
bot2: python app/bots/admin_bot.py $PORT
web: gurnicon -w 4 bot:app