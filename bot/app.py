import os
import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from decouple import config

try:
    from bot.helpers.app_config import AppConfigs
except ImportError:
    from helpers.app_config import AppConfigs

uri = config('DATABASE_URL')
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)
app.secret_key = AppConfigs().get_secret_key()


@app.route('/')
def get_info(word):

    url = 'https://api.dictionaryapi.dev/api/v2/entries/en/{}'.format(word)

    response = requests.get(url)

# return a custom response if an invalid word is provided
    if response.status_code == 404:
        error_response = 'We are not able to provide any information about your word. Please confirm that the word is ' \
                         'spelled correctly or try the search again at a later time.'
        return error_response

    data = response.json()[0]

    print(data)
    return data


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
