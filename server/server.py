from flask import Flask, render_template, request, jsonify
import sqlite3
from sys import argv

app = Flask(__name__)

DB = '../pow.db'

@app.route('/stations', methods=['GET'])
def stations():
    conn = sqlite3.connect(app.config['DB'])
    c = conn.cursor()
    q = c.execute('SELECT * FROM {};'.format('stations'))
    r = [dict((q.description[i][0], value) \
               for i, value in enumerate(row)) for row in q.fetchall()]
    return jsonify(r)

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        print(request)
    return render_template("index.html")


if __name__ == "__main__":
    try:
        app.config['DB'] = argv[1]
    except IndexError:
        print("usage: server.py [database_file]")
        exit(1)
    app.run(host='0.0.0.0', port=8080, debug=True)
