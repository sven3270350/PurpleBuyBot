release: export FLASK_APP=bot:app && flask db upgrade --directory bot/migrations
bot1: python bot/bots/public_bot.py $PORT
bot2: python bot/bots/admin_bot.py $PORT
web: gurnicon -w 4 bot:app