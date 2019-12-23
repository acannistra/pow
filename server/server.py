from flask import Flask, render_template, send_file, request, jsonify, make_response
import sqlite3
import sys
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
plt = matplotlib.pyplot 
sys.path.append('..')
from util import snowtools, dbtools

app = Flask(__name__)

DB = '../pow.db'


def compute_pow(params):
    station = dbtools.get_station(app.config['DB'], params['station'])

    snow = snowtools.get_snow_df(snowtools.get_nwac_v2_url(station['description']))
    pow = snowtools.find_pow(snow, int(params['snowfall_threshold']), int(params['accumulation_period']))
    return pow

@app.route("/pow")
def pow():
    params = dbtools.get_params(app.config['DB'])

    pow = compute_pow(params)

    most_recent = pow.iloc[-1]
    r = params.copy()
    r['is_pow'] = str(most_recent.is_pow)
    r['period_accumulation'] = most_recent.accum
    r['measurement_time'] = most_recent.name
    return(jsonify(r))

@app.route("/pow/plot")
def plotpow():
    params = dbtools.get_params(app.config['DB'])

    pow = compute_pow(params)

    fig = snowtools.pow_history(pow, params['station'])
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    return send_file(buf, mimetype='image/png')
    # plt.show(fig)



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
        dbtools.update_params(app.config['DB'], {
            'station': request.form.get('location'),
            'snowfall_thresh': request.form.get('snowfall_thresh'),
            'accumulation_period': request.form.get('accumulation_period')
        })
    return render_template("index.html", **dbtools.get_params(app.config['DB']))


if __name__ == "__main__":
    try:
        app.config['DB'] = sys.argv[1]
    except IndexError:
        print("usage: server.py [database_file]")
        exit(1)
    app.run(host='0.0.0.0', port=8080, debug=True)
