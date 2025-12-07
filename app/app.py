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

@APP.route('/shows/')
def shows_index():
    # Get some basic stats
    stats = db.execute("""
        SELECT 
            COUNT(*) as total_shows,
            AVG(metascore) as avg_metascore,
            AVG(userscore) as avg_userscore
        FROM show
        WHERE metascore IS NOT NULL AND userscore IS NOT NULL
    """).fetchone()
    
    # Get a few recent or random shows
    sample_shows = db.execute("""
        SELECT title, metascore, userscore
        FROM show
        WHERE metascore IS NOT NULL AND userscore IS NOT NULL
        ORDER BY RANDOM()
        LIMIT 5
    """).fetchall()
    
    return render_template('shows_index.html',
                         stats=stats,
                         sample_shows=sample_shows,
                         title="Shows Database")


"""

"""
@APP.route('/shows/top-discrepancies')
def top_discrepancies():
    results = db.execute("""
        SELECT
          title,
          metascore,
          userscore,
          metascore_count,
          userscore_count,
          ABS(metascore - userscore) AS discrepancy,
          CASE 
            WHEN userscore_count < 10 THEN 'Low User Reviews'
            WHEN metascore_count < 5 THEN 'Low Critic Reviews'
            ELSE 'Sufficient Reviews'
          END AS reliability,
          ABS(metascore - userscore) * 
            MIN(1.0, userscore_count / 20.0) *
            MIN(1.0, metascore_count / 10.0)
          AS weighted_discrepancy
        FROM show
        WHERE
          metascore IS NOT NULL 
          AND userscore IS NOT NULL
        ORDER BY
          weighted_discrepancy DESC,
          discrepancy DESC
        LIMIT 50;
    """).fetchall()

    return render_template('top_discrepancies.html',
                           shows = results,
                           title = "Top 10 Biggest Score Gaps")

@APP.route('/people/writer-directors')
def writer_directors():
    # Get statistical overview first
    stats = db.execute("""
        WITH wd AS (
            SELECT p.id, COUNT(DISTINCT s.id) AS shows_count
            FROM person p
            JOIN wrote w ON p.id = w.person_id
            JOIN directed d ON p.id = d.person_id AND w.show_id = d.show_id
            JOIN show s ON s.id = w.show_id
            GROUP BY p.id
        )
        SELECT 
            COUNT(*) AS total_people,
            AVG(shows_count) AS avg_shows,
            SUM(CASE WHEN shows_count = 1 THEN 1 ELSE 0 END) AS one_show_wonders,
            SUM(CASE WHEN shows_count >= 3 THEN 1 ELSE 0 END) AS frequent_collaborators
        FROM wd
    """).fetchone()
    
    # Get the writer-directors
    results = db.execute("""
        SELECT 
            p.name,
            COUNT(DISTINCT s.id) AS shows_count,
            ROUND(AVG(s.metascore), 1) AS avg_metascore,
            ROUND(AVG(s.userscore), 1) AS avg_userscore,
            MAX(s.metascore) AS best_score,
            MIN(s.metascore) AS worst_score
        FROM person p
        JOIN wrote w ON p.id = w.person_id
        JOIN directed d ON p.id = d.person_id AND w.show_id = d.show_id
        JOIN show s ON s.id = w.show_id
        WHERE s.metascore IS NOT NULL
        GROUP BY p.id, p.name
        ORDER BY 
            CASE 
                WHEN COUNT(DISTINCT s.id) >= 3 THEN 0
                ELSE 1
            END,
            avg_metascore DESC,
            shows_count DESC
        LIMIT 30
    """).fetchall()
    
    return render_template('writer_directors.html',
                         people=results,
                         stats=stats,
                         title="Writer-Directors Analysis")
