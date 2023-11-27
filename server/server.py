import os
from flask import Flask, render_template, send_file, request, jsonify, make_response
import sqlite3
import sys
from io import BytesIO
import matplotlib
import json
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.append('.')
from util import snowtools, dbtools

POW_NWAC_STATIONS_FILE = os.environ.get("POW_NWAC_STATIONS_FILE", "nwac-stations.json")

app = Flask(__name__)


class APIError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(APIError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def parse_request(request):
    station = request.args.get("station")
    threshold = int(request.args.get('threshold'))
    period = int(request.args.get('period'))

    try:
        stations = json.load(open(POW_NWAC_STATIONS_FILE))
        id = [_i['nwac_id'] for _i in stations if _i['name'].lower() == station.lower()][0]
    except IndexError:
        raise APIError(f"Station \"{station}\" not found. See /stations.", status_code=404)


    return (id, threshold, period)

def compute_pow(staid, thresh, period):
    snow = snowtools.get_snow_df(staid, period*4)
    pow = snowtools.find_pow_2(snow, int(thresh), int(period))
    return pow

@app.route("/pow/")
def pow():
    staid, threshold, period = parse_request(request)

    pow = compute_pow(staid, threshold, period)

    most_recent = pow.iloc[-1]
    r = request.args.copy()
    r['is_pow'] = str(most_recent.is_pow)
    r['period_accumulation'] = most_recent.accum
    r['measurement_time'] = most_recent.name
    return(jsonify(r))

@app.route("/pow/plot")
def plotpow():
    staid, threshold, period = parse_request(request)

    pow = compute_pow(staid, threshold, period)

    fig = snowtools.pow_history(pow, staid)
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    return send_file(buf, mimetype='image/png')
    # plt.show(fig)


@app.route('/stations', methods=['GET'])
def stations():
    r = json.load(open(POW_NWAC_STATIONS_FILE))
    return jsonify(r)



if __name__ == "__main__":        
    app.run(host='0.0.0.0', port=8080, debug=True)
