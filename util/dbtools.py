import sqlite3

def update_params(db, params):
    db_conn = sqlite3.connect(db)
    db_conn.executemany("INSERT INTO params VALUES (?, ?)", [
        ("station", params['station']),
        ("snowfall_threshold", params['snowfall_thresh']),
        ("accumulation_period", params['accumulation_period'])
    ])
    db_conn.commit()

def get_params(db):
    db_conn = sqlite3.connect(db)
    q = db_conn.execute("SELECT * FROM params;")
    return(dict(q.fetchall()))

def get_station(db, name):
    db_conn = sqlite3.connect(db)
    q = db_conn.execute("SELECT * FROM stations where name = ?", (name,))
    r = [dict((q.description[i][0], value) \
           for i, value in enumerate(row)) for row in q.fetchall()]
    return r[0]
