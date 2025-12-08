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
            (SELECT COUNT(*) AS Actors FROM acted)
        JOIN
            (SELECT COUNT(*) AS Directors FROM directed)
        JOIN
            (SELECT COUNT(*) AS Writers FROM wrote)
        JOIN
            (SELECT COUNT(*) AS Creators FROM created)
        JOIN
            (SELECT COUNT(*) AS Companies FROM productionCompany)
        JOIN 
            (SELECT AVG(metascore) AS avg_metascore FROM show WHERE metascore IS NOT NULL)
        JOIN
            (SELECT AVG(userscore) AS avg_userscore FROM show WHERE userscore IS NOT NULL)
    ''').fetchone()
    logging.info(stats)
    return render_template('shows_index.html', stats = stats)

@APP.route('/q1')
def query1():
    # Ator/es com mais categorias
    q1 = db.execute ('''
        SELECT person.name, COUNT(genre.show_id) AS n
        FROM person
        JOIN acted ON person.id = acted.person_id
        JOIN genre ON acted.show_id = genre.show_id
        GROUP BY person.name
        ORDER BY n
        LIMIT 1
    ''').fetchall()
    return render_template('q1.html', q1 = q1)

@APP.route('/q2')
def query2():
    # Ator/es com mais categorias
    q2 = db.execute ('''
        SELECT genre_name, title, metascore,
        CASE WHEN rnkBest = 1 THEN 'Best' ELSE 'Worst' END as rating_type
        FROM (
            SELECT
                s.title,
                g.genre_name,
                s.metascore,
            ROW_NUMBER() OVER (
            PARTITION BY g.genre_name
            ORDER BY s.metascore DESC, s.title) rnkBest,
            ROW_NUMBER() OVER (
                PARTITION BY g.genre_name
                ORDER BY s.metascore ASC, s.title) rnkWorst
            FROM show s
            JOIN genre g ON g.show_id = s.id
            WHERE s.metascore IS NOT NULL
        ) x
        WHERE x.rnkBest = 1 OR x.rnkWorst = 1
        ORDER BY genre_name, rating_type ASC;
    ''').fetchall()
    return render_template('q2.html', q2 = q2)

@APP.route('/q3')
def query3():
    # O filme com mais descrepância entre metaScore e userScore
    q3 = db.execute('''
        SELECT
        title,
        metascore,
        userscore,
        ABS(metaScore - (userScore * 10)) AS Discrepancia
        FROM show
        WHERE
        metaScore IS NOT NULL AND userScore IS NOT NULL
        ORDER BY
        Discrepancia DESC
        LIMIT 1;
    ''').fetchall()
    return render_template('top_discrepancies.html', q3 = q3)

@APP.route('/q4')
def query4():
    # OS 3 atores que fizeram mais shows
    q4 = db.execute('''
        SELECT person.name, COUNT(show.id) AS num
        FROM person 
        JOIN acted ON person.id = acted.person_id
        JOIN show ON acted.show_id = show.id 
        GROUP BY person.name
        ORDER BY num desc
        LIMIT 3;
    ''').fetchall()
    return render_template('q4.html', q4 = q4)

@APP.route('/q5')
def query5():
    # Pessoas que escreveram e dirigiram o mesmo show
    q5 = db.execute('''
        SELECT 
            p.name,
            s.title AS show_title
        FROM wrote w
        JOIN directed d 
        ON w.show_id = d.show_id AND w.person_id = d.person_id
        JOIN person p 
        ON p.id = w.person_id
        JOIN show s 
        ON s.id = w.show_id;
    ''').fetchall()
    return render_template('writer_directors.html', q5 = q5)

@APP.route('/q6')
def query6():
    # Top 5 shows com mais temporadas
    q6 = db.execute('''
        SELECT show.title, show.num_seasons
        FROM show
        ORDER BY num_seasons desc
        LIMIT 5;
    ''').fetchall()
    return render_template('q6.html', q6 = q6)

@APP.route('/q7')
def query7():
    # Criadores, shows, e companhias de produção
    q7 = db.execute('''
        SELECT 
            p.name AS creator,
            s.title AS show_title,
            pc.company AS production_company
            FROM created c
        JOIN person p 
        ON p.id = c.person_id
        JOIN show s 
        ON s.id = c.show_id
        LEFT JOIN producedBy pb 
        ON pb.show_id = s.id
        LEFT JOIN productioncompany pc 
        ON pc.id = pb.producer_id;
    ''').fetchall()
    return render_template('q7.html', q7 = q7)