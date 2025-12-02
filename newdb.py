import pandas as pd
import sqlite3

df = pd.read_csv("tv_shows.csv")
conn = sqlite3.connect("tvshows.db")
cur = conn.cursor()

# Create tables according to the proposed model
cur.executescript ("""
    DROP TABLE IF EXISTS show;
    DROP TABLE IF EXISTS genre;
    DROP TABLE IF EXISTS person;
    DROP TABLE IF EXISTS acted;
    DROP TABLE IF EXISTS directed;
    DROP TABLE IF EXISTS created;
    DROP TABLE IF EXISTS wrote;
    DROP TABLE IF EXISTS productionCompany;
    DROP TABLE IF EXISTS producedBy;

    CREATE TABLE show (
        id INTEGER PRIMARY KEY,
        title TEXT,
        releaseDate TEXT,
        rating TEXT,
        duration REAL,
        tagline TEXT,
        description TEXT,
        num_seasons INTEGER,
        metascore INTEGER,
        metascore_count INTEGER,
        metascore_sentiment TEXT,
        userscore INTEGER,
        userscore_count INTEGER,
        userscore_sentiment TEXT
    );

    CREATE TABLE genre (
        show_id INTEGER,
        genre_name TEXT,
        FOREIGN KEY (show_id) REFERENCES show(id)
    );

    CREATE TABLE person (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    );

    CREATE TABLE productionCompany (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT
    );

    CREATE TABLE acted (
        show_id INTEGER,
        person_id INTEGER,
        FOREIGN KEY (show_id) REFERENCES show(id),
        FOREIGN KEY (person_id) REFERENCES person(id)
    );

    CREATE TABLE directed (
        show_id INTEGER,
        person_id INTEGER,
        FOREIGN KEY (show_id) REFERENCES show(id),
        FOREIGN KEY (person_id) REFERENCES person(id)
    );

    CREATE TABLE created (
        show_id INTEGER,
        person_id INTEGER,
        FOREIGN KEY (show_id) REFERENCES show(id),
        FOREIGN KEY (person_id) REFERENCES person(id)
    );

    CREATE TABLE wrote (
        show_id INTEGER,
        person_id INTEGER,
        FOREIGN KEY (show_id) REFERENCES show(id),
        FOREIGN KEY (person_id) REFERENCES person(id)
    );

    CREATE TABLE producedBy (
        show_id INTEGER,
        producer_id INTEGER,
        FOREIGN KEY (show_id) REFERENCES show(id),
        FOREIGN KEY (producer_id) REFERENCES productionCompany(id)
    );
""")
conn.commit()

# Assign values to the table "show"
show_columns = [
    "id", "title", "releaseDate", "rating", "duration", "tagline",
    "num_seasons", "metascore", "metascore_count", "metascore_sentiment",
    "userscore", "userscore_count", "userscore_sentiment"
]

df[[
    "id", "title", "releaseDate", "rating", "duration", "tagline","description",
    "num_seasons", "metascore", "metascore_count", "metascore_sentiment",
    "userscore", "userscore_count", "userscore_sentiment"
]].to_sql("show", conn, if_exists="append", index=False)

# Assign values to the table "genre"
all_genres = (
    df["genres"].str.split(",").explode()
    .str.strip()
    .unique()
)

for g in all_genres:
    if g:
        cur.execute("INSERT OR IGNORE INTO genre (genre_name) VALUES (?)", (g,))
conn.commit()

# Assign values to the table "productionCompany"
all_companies = (
    df["production_companies"].str.split(",").explode()
    .str.strip()
    .unique()
)

for c in all_companies:
    cur.execute("INSERT OR IGNORE INTO productionCompany (company) VALUES (?)", (c,))
conn.commit()

# Assign values to the table "person" and their respective roles
def extract_people (series):
    ppl = (
        series.str.split(",").explode().str.strip()
    )
    return [p for p in ppl.unique() if p]

all_people = set()
all_people.update(extract_people(df["top_cast"]))
all_people.update(extract_people(df["director"]))
all_people.update(extract_people(df["writer"]))
all_people.update(extract_people(df["created_by"]))

for people in all_people:
    cur.execute("INSERT OR IGNORE INTO person (name) VALUES (?)", (people,))
conn.commit()

def people_id (name):
    cur.execute("SELECT id FROM person WHERE name = ?", (name,))
    row = cur.fetchone()
    return row[0] if row else None

def relation (table, show_id, people_str):
    people = [p.strip() for p in str(people_str).split(",") if p.strip()]
    for person in people:
        person_id = people_id(person)
        if person_id:
            cur.execute (
                f"INSERT INTO {table} (show_id, person_id) VALUES (?, ?)", 
                (show_id, person_id)
            )
for _, row in df.iterrows():
    show_id = row["id"]
    relation("acted", show_id, row["top_cast"])
    relation("directed", show_id, row["director"])
    relation("wrote", show_id, row["writer"])
    relation("created", show_id, row["created_by"])
conn.commit()
conn.close()