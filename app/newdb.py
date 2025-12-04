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
    DROP TABLE IF EXISTS acted;c
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
        userscore INTEGER,
        userscore_count INTEGER,

        metascore_sentiment TEXT GENERATED ALWAYS AS (
            CASE 
                WHEN metascore IS NULL THEN 'No score'
                WHEN metascore >= 81 THEN 'Universal acclaim'
                WHEN metascore >= 61 THEN 'Generally favorable'
                WHEN metascore >= 40 THEN 'Mixed or average'
                WHEN metascore >= 20 THEN 'Generally unfavorable'
                ELSE 'Overwhelming dislike'
            END
        ) VIRTUAL,
            
        userscore_sentiment TEXT GENERATED ALWAYS AS (
            CASE 
                WHEN userscore IS NULL THEN 'No score'
                WHEN userscore >= 81 THEN 'Universal acclaim'
                WHEN userscore >= 61 THEN 'Generally favorable'
                WHEN userscore >= 40 THEN 'Mixed or average'
                WHEN userscore >= 20 THEN 'Generally unfavorable'
                ELSE 'Overwhelming dislike'
            END
        ) VIRTUAL
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
    "num_seasons", "metascore", "metascore_count",
    "userscore", "userscore_count"
]

df[[
    "id", "title", "releaseDate", "rating", "duration", "tagline","description",
    "num_seasons", "metascore", "metascore_count",
    "userscore", "userscore_count"
]].to_sql("show", conn, if_exists="append", index=False)

# Assign values to the table "genre"
for _, row in df.iterrows():
    show_id = row["id"]
    genres = str(row["genres"]).split(",") if pd.notna(row["genres"]) else []
    for genre_name in genres:
        genre_name = genre_name.strip()
        if genre_name:
            cur.execute(
                "INSERT INTO genre (show_id, genre_name) VALUES (?, ?)",
                (show_id, genre_name)
            )
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

# Assing values to the table "producedBy"
def producer_id(company_name):
    cur.execute("SELECT id FROM productionCompany WHERE company = ?", (company_name,))
    row = cur.fetchone()
    return row[0] if row else None

for _, row in df.iterrows():
    show_id = row["id"]
    companies = str(row["production_companies"]).split(",") if pd.notna(row["production_companies"]) else []
    for company_name in companies:
        company_name = company_name.strip()
        if company_name:
            prod_id = producer_id(company_name)
            if prod_id:
                cur.execute(
                    "INSERT INTO producedBy (show_id, producer_id) VALUES (?, ?)",
                    (show_id, prod_id)
                )
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