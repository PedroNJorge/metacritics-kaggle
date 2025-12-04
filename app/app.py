import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from flask import render_template, Flask
import logging
import db

APP = Flask(__name__)

# Start page
@APP.route('/')
def index():
    info = {}
    stats = db.execute ('''
        SELECT * FROM 
            (SELECT COUNT(*) FROM SHOWS)
    ''')
