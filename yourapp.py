from app import app
from flask import Flask, request
from config import Config
import json

app.config.from_object(Config)

if __name__ == '__main__':
    app.run()