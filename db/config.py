import sqlite3
import json
import click


@click.group()
def cli(**kwargs):
    pass

@cli.command()
@click.argument('name', default='pow.db')
def init(**kwargs):
    print("Creating sqlite3 database [{}]...".format(kwargs['name']))
    conn = sqlite3.connect(kwargs['name'])
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stations
                 (name text, description text, url text, lon float, lat float,
                 CONSTRAINT name PRIMARY KEY (name));''')
    conn.commit()
    conn.close()

@cli.command()
@click.argument('db')
@click.option('--name', '-n', help="Station Name")
@click.option('--url', help="URL of wx data")
@click.option('--description', '--desc', help="Station Description")
@click.option('--location', help="(lat,lon)")
def addStation(**kwargs):
    lat, lon = kwargs['location'].strip().split(',')

    conn = sqlite3.connect(kwargs['db'])
    c = conn.cursor()
    command = '''INSERT INTO stations VALUES (?, ?, ?, ?, ?)'''
    c.execute(command, (
        kwargs['name'],
        kwargs['description'],
        kwargs['url'],
        float(lat),
        float(lon)
    ))
    conn.commit()
    conn.close()

@cli.command()
@click.argument('db')
@click.argument('name')
def dropStation(**kwargs):
    conn = sqlite3.connect(kwargs['db'])
    c = conn.cursor()
    command = "DELETE FROM stations WHERE name = ?"
    c.execute(command, (kwargs['name'], ))
    conn.commit()
    conn.close()

@cli.command('list')
@click.argument("db")
def listStations(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    q = c.execute("SELECT * from stations;")
    r = [dict((q.description[i][0], value) \
               for i, value in enumerate(row)) for row in q.fetchall()]
    print(json.dumps(r))





if __name__ == '__main__':
    cli()
