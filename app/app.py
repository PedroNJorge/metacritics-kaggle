import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from flask import render_template, Flask
import logging
import db

APP = Flask(__name__)

# Start page
@APP.route('/')
def index():
    stats = {}
    stats = db.execute ('''
        SELECT * FROM 
            (SELECT COUNT(*) AS Shows FROM show)
        JOIN
            (SELECT COUNT(*) AS People FROM person)
    ''').fetchone()
    logging.info(stats)
    return render_template('index.html', stats = stats)