import sqlite3
import json
import click


@click.group()
def cli(**kwargs):
    pass

@cli.command()
@click.argument('name', default='pow.db')
@click.option("--file", help="JSON File containing stations to load.")
def init(**kwargs):
    print("Creating sqlite3 database [{}]...".format(kwargs['name']))
    conn = sqlite3.connect(kwargs['name'])
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stations
                 (name text, description text, elevation int, data_url text, snow_field text, lon float, lat float,
                 CONSTRAINT name PRIMARY KEY (name));''')
    c.execute('''CREATE TABLE IF NOT EXISTS params
                 (name text, value text);''')

    if kwargs['file']:
        stations = json.load(open(kwargs['file']))
        for station in stations:
            load_command = "INSERT INTO stations VALUES (?, ?, ?, ?, ?, ?, ?)"
            print("Loading Station {}".format(station.get('name')))
            c.execute(load_command, (
                station.get('name'),
                station.get('desc', station.get('nwac_id')),
                station.get('elevation', -1),
                station.get('url', None),
                station.get('snow_field', 'snow_depth'),
                station.get('lon'),
                station.get('lat')
            ))

        c.executemany("INSERT INTO params VALUES (?, ?)", [
            ("station", stations[0].get('name')),
            ("snowfall_threshold", 6),
            ("accumulation_period", 24)
        ])
    conn.commit()
    conn.close()

@cli.command()
@click.argument('db')
@click.option('--name', '-n', help="Station Name")
@click.option('--data_url', '--url', help="URL of wx data")
@click.option("--snow_field", '--field', help="Field name in data CSV containing hourly snowfall amounts.")
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
