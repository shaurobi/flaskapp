import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.flaskenv'))
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    secretID = os.environ.get('SECRET_ID')
    clientID = os.environ.get('CLIENT_ID')
    redirectURI = os.environ.get('REDIRECT_URI')
    WTF_CSRF_ENABLED = True
    # Disable/Enable debugging
    DEBUG = True
    