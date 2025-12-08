import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from flask import render_template, Flask, request
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

# Search a show by its title
@APP.route('/search')
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type = int)
    per_page = 20
    offset = (page - 1) * per_page

    if query:
        count_result = db.execute ('''
            SELECT COUNT(*) AS total
            FROM show
            WHERE title LIKE ?
        ''', ('%' + query + '%',)).fetchone()
        total = count_result['total']

        result = db.execute('''
            SELECT id, title, releaseDate, rating, metascore,
                userscore, num_seasons
            FROM show
            WHERE title LIKE ?
            ORDER BY title
            LIMIT ? OFFSET ?
        ''',('%' + query + '%', per_page, offset)).fetchall()  
        total_pages = (total + per_page - 1) // per_page

    else: 
        results = []
        total = 0
        total_pages = 0
    return render_template ('search.html', query = query,
                                           results = results,
                                           page = page,
                                           total_pages = total_pages,
                                           total = total)

# Navigation through all shows
@APP.route('/show/')
def show():
    page = request.args.get('page', 1, type = int)
    per_page = 20
    offset = (page - 1) * per_page
    count_result = db.execute ('''
        SELECT COUNT (*) AS total
        FROM show
    ''').fetchone()
    total = count_result['total']

    shows_list = db.execute('''
        SELECT *
        FROM show
        ORDER BY title
        LIMIT ? OFFSET ?
    ''', (per_page, offset)).fetchall()
    total_pages = (total + per_page - 1) // per_page

    return render_template('show.html', shows = shows_list,
                                              page = page,
                                              total_pages = total_pages,
                                              total = total)

# Show info
@APP.route('/show/<int:show_id>')
def show_detail(show_id):
    show = db.execute('''
        SELECT * 
        FROM show
        WHERE id = ?
    ''', (show_id,)).fetchone()
    if not show: 
        return "Show not found", 404
    
    # Get genres
    genres = db.execute('''
        SELECT genre_name 
        FROM genre
        WHERE show_id = ?
    ''', (show_id,)).fetchall()

    # Get production companies
    companies = db.execute('''
        SELECT company
        FROM productionCompany c
        JOIN producedBy p ON c.id = p.producer_id
        WHERE p.show_id = ?
    ''', (show_id,)).fetchall()

    # Get actors
    actors = db.execute('''
        SELECT p.name, p.id
        FROM person p
        JOIN acted a ON p.id = a.person_id
        WHERE a.show_id = ?
    ''', (show_id,)).fetchall()

    # Get writers
    writers = db.execute('''
        SELECT p.name, p.id
        FROM person p
        JOIN wrote w ON p.id = w.person_id
        WHERE w.show_id = ?
    ''', (show_id,)).fetchall()

    # Get directors
    directors = db.execute('''
        SELECT p.name, p.id
        FROM person p
        JOIN directed d ON p.id = d.person_id
        WHERE d.show_id = ?
    ''', (show_id,)).fetchall()

    # Get creators
    creators = db.execute('''
        SELECT p.name
        FROM person p
        JOIN created c ON p.id = c.person_id
        WHERE c.show_id = ?
    ''', (show_id,)).fetchall()

    return render_template('show_detail.html', show = show,
                                               genres = genres,
                                               companies = companies,
                                               actors = actors,
                                               writers = writers,
                                               directors = directors,
                                               creators = creators)

# Navigation through all shows
@APP.route('/person/')
def person():
    page = request.args.get('page', 1, type = int)
    per_page = 20
    offset = (page - 1) * per_page
    count_result = db.execute ('''
        SELECT COUNT (*) AS total
        FROM person
    ''').fetchone()
    total = count_result['total']

    people_list = db.execute('''
        SELECT p.*,
            COUNT(DISTINCT a.show_id) as acted_count,
            COUNT(DISTINCT d.show_id) as directed_count,
            COUNT(DISTINCT w.show_id) as wrote_count,
            COUNT(DISTINCT c.show_id) as created_count
        FROM person p
        LEFT JOIN acted a ON p.id = a.person_id
        LEFT JOIN directed d ON p.id = d.person_id
        LEFT JOIN wrote w ON p.id = w.person_id
        LEFT JOIN created c ON p.id = c.person_id
        GROUP BY p.id, p.name
        ORDER BY p.name
        LIMIT ? OFFSET ?
    ''', (per_page, offset)).fetchall()
    total_pages = (total + per_page - 1) // per_page

    return render_template('person.html', people = people_list,
                                              page = page,
                                              total_pages = total_pages,
                                              total = total)
# Person info
@APP.route('/person/<int:person_id>')
def person_detail(person_id):
    person = db.execute('''
        SELECT *
        FROM person
        WHERE id = ?
    ''', (person_id,)).fetchone()
    
    if not person:
        return "Person not found", 404
    
    # Acted in (with scores)
    acted_shows = db.execute('''
        SELECT show.id, show.title, show.releaseDate, 
               show.metascore, show.userscore
        FROM show
        JOIN acted ON show.id = acted.show_id
        WHERE acted.person_id = ?
        ORDER BY show.releaseDate DESC, show.title
    ''', (person_id,)).fetchall()

    # Wrote (with scores)
    written_shows = db.execute('''
        SELECT show.id, show.title, show.releaseDate,
               show.metascore, show.userscore
        FROM show
        JOIN wrote ON show.id = wrote.show_id
        WHERE wrote.person_id = ?
        ORDER BY show.releaseDate DESC, show.title
    ''', (person_id,)).fetchall()

    # Directed (with scores)
    directed_shows = db.execute('''
        SELECT show.id, show.title, show.releaseDate,
               show.metascore, show.userscore
        FROM show
        JOIN directed ON show.id = directed.show_id
        WHERE directed.person_id = ?
        ORDER BY show.releaseDate DESC, show.title
    ''', (person_id,)).fetchall()

    # Created (with scores)
    created_shows = db.execute('''
        SELECT show.id, show.title, show.releaseDate,
               show.metascore, show.userscore
        FROM show
        JOIN created ON show.id = created.show_id
        WHERE created.person_id = ?
        ORDER BY show.releaseDate DESC, show.title
    ''', (person_id,)).fetchall()

    # Get average scores
    stats = db.execute('''
        SELECT 
            COUNT(DISTINCT a.show_id) as acted_total,
            COUNT(DISTINCT d.show_id) as directed_total,
            COUNT(DISTINCT w.show_id) as wrote_total,
            COUNT(DISTINCT c.show_id) as created_total,
            ROUND(AVG(CASE WHEN a.show_id IS NOT NULL THEN show.metascore END), 1) as avg_acted_metascore,
            ROUND(AVG(CASE WHEN d.show_id IS NOT NULL THEN show.metascore END), 1) as avg_directed_metascore,
            ROUND(AVG(CASE WHEN w.show_id IS NOT NULL THEN show.metascore END), 1) as avg_wrote_metascore,
            ROUND(AVG(CASE WHEN c.show_id IS NOT NULL THEN show.metascore END), 1) as avg_created_metascore
        FROM person p
        LEFT JOIN acted a ON p.id = a.person_id
        LEFT JOIN directed d ON p.id = d.person_id
        LEFT JOIN wrote w ON p.id = w.person_id
        LEFT JOIN created c ON p.id = c.person_id
        LEFT JOIN show ON show.id IN (a.show_id, d.show_id, w.show_id, c.show_id)
        WHERE p.id = ?
    ''', (person_id,)).fetchone()

    return render_template('person_detail.html', 
                         person=person,
                         acted_shows=acted_shows,
                         written_shows=written_shows,
                         directed_shows=directed_shows,
                         created_shows=created_shows,
                         stats=stats,
                         title=f"{person['name']}")


# Production company info
@APP.route('/company/<int:company_id>')
def company_details(company_id):
    company = db.execute('''
        SELECT company
        FROM productionCompany
        WHERE id = ?
    ''', (company_id,)).fetchone()
    if not company:
        return "Production company not found", 404
    
    # Produced shows
    shows_produced = db.execute('''
        SELECT show.title
        FROM show
        JOIN producedBy p on show.id = p.show_id
        WHERE p.producer_id = ?
    ''', (company_id,)).fetchall()

    return render_template('company_detail.html', company = company,
                                                  shows_produced = shows_produced)

# Genres info (with pagination)
@APP.route('/genre/<genre_name>')
def genre_detail(genre_name):
    page = request.args.get('page', 1, type = int)
    per_page = 20
    offset = (page - 1) * per_page
    count_result = db.execute('''
        SELECT COUNT(*) AS total 
        FROM show s
        JOIN genre g on s.id = g.show_id
        WHERE g.genre_name = ?
    ''', (genre_name,)).fetchone()
    total = count_result['total']

    # Shows of a certain genre
    shows = db.execute('''
        SELECT s.id, s.title, s.releaseDate, s.metascore, s.userscore
                       s.num_seasons
        FROM show s
        JOIN genre g on s.id = g.show_id
        WHERE g.genre_name = ?
        ORDER BY s.title
        LIMIT ? OFFSET ?
    ''', (genre_name, per_page, offset)).fetchall()
    total_pages = (total + per_page - 1) // per_page

    return render_template('genre_detail.html',
                            genre_name=genre_name,
                            shows=shows,
                            page=page,
                            total_pages=total_pages,
                            total=total)

# Queries 1 - 10
# Query 3: Shows with the most discrepancies between userscore and metascore
@APP.route('/show/top-discrepancies')
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

# Query 5 : People who wrote and directed the same show
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
    # Show com melhor e pior rating dentro de cada categoria
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
