import sqlite3
import requests
import click
import sys

sys.path.append('..')

def get_params_db(db, table='params'):
    """
        Get POW alerting parameters from database.
    """
    conn = sqlite3.connect(db)
    c = conn.cursor()
    q = c.execute('SELECT * FROM {};'.format(table))
    r = [dict((q.description[i][0], value) \
               for i, value in enumerate(row)) for row in q.fetchall()]
    return(r)

@click.command()
@click.argument('DB')
def daemon(db):
    print("Loading parameters from db [{}]".format(db))
    print(get_params_db(db))
    pass


if __name__ == '__main__':
    daemon()
