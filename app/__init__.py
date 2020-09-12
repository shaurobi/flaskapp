from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)
app.jinja_env.filters['zip'] = zip

from app import routes