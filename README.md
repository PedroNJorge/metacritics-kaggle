# TV Shows Database Explorer
This project was developed in the Databases subject, in the 1st semester of the 2nd year of BSc in AI & DS.
It's a Flask-based web application for exploring TV shows, people, genres, production companies, and industry relationships using a SQLite database.
The project provides a searchable interface for browsing show details, cast and crew information, production companies, genres, and a collection of advanced SQL query examples.

## Features

* Browse TV shows with pagination
* Search shows by title or ID
* Detailed show pages with:
  * Genres
  * Production companies
  * Cast and crew
  * Ratings and metadata
  * Actors
  * Writers
  * Directors
  * Creators
* Browse production companies and genres
* Relationship views between entities
* Prebuilt analytical SQL queries
* SQLite-backed persistence layer
* Server-side rendered UI using Flask templates

## Tech Stack

* **Backend:** Python, Flask
* **Database:** SQLite
* **Frontend:** HTML, CSS, Jinja2 Templates
* **Server:** Flask development server

## Project Structure

```text
app/
├── app.py                     # Main Flask application and routes
├── server.py                  # Application entry point
├── db.py                      # Database connection utilities
├── newdb.py                   # Database-related helper script
├── test_db_connection.py      # Database connection test
├── tvshows.db                 # SQLite database
├── static/                    # CSS stylesheets
│   ├── base.css
│   ├── detail_simple.css
│   ├── genre.css
│   ├── index.css
│   └── person.css
└── templates/                 # Jinja2 templates
    ├── base.html
    ├── index.html
    ├── show.html
    ├── show_detail.html
    ├── person.html
    └── ...
```

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
```

Activate the environment:

**Windows**

```bash
venv\Scripts\activate
```

**macOS / Linux**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install flask
```

## Running the Application

From the `app` directory:

```bash
python server.py
```

The application will start on:

```text
http://localhost:9000
```

## Database

The project uses a SQLite database file:

```text
tvshows.db
```

Database access is managed through `db.py`, which:

* Establishes the SQLite connection
* Registers helper SQL functions
* Executes parameterized queries
* Handles cursor management

## Main Routes

| Route                 | Description                       |
| --------------------- | --------------------------------- |
| `/`                   | Dashboard and statistics overview |
| `/show/`              | Browse all TV shows               |
| `/show/<id>`          | Detailed show information         |
| `/person/`            | Browse people                     |
| `/person/<id>`        | Person details                    |
| `/genre/`             | Browse genres                     |
| `/genre/<genre_name>` | Genre-specific shows              |
| `/productionCompany/` | Production companies              |
| `/queries/`           | Advanced SQL query examples       |

## Search Functionality

The application supports:

* Search by show title
* Search by show ID
* Automatic redirects for exact matches
* Partial title matching using SQL `LIKE`
* Paginated browsing

## Example Queries

The project includes multiple advanced SQL query routes that answer the following questions:
- Which actor(s) appear in the most categories?
- Which show has the highest (and lowest) rating within each category?
- Which film has the greatest discrepancy between Metascore and User Score?
- Top 10 actors that participated in more shows
- Top 30 people who wrote and directed the same show
- The 5 longest shows (with more seasons)
- Top 20 pairs (director, actor) that worked together the most
- Best show per decade
- Average score per genre
- Top 5 shows with the biggest crew
- Most popular genre per decade
- Most successful pairs of genres
- Most famous production companies
- Show quality vs number of seasons comparison
- Show quality variation

## Development Notes

* The application uses a global SQLite connection object.
* SQL queries are executed using parameterized statements.
* Templates are rendered with Jinja2.
* Styling is organized into modular CSS files.

Built with:

* Flask
* SQLite
* Jinja2
* Python
