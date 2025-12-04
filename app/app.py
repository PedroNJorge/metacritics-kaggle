import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from flask import render_template, Flask
import logging
import db

APP = Flask(__name__)

# Start page
@APP.route('/shows/')
def shows():
    shows = db.execute('''
        SELECT show.title
        FROM show
    ''').fetchall()
    return render_template('shows', shows = shows)