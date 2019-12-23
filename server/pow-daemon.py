from flask import Flask, render_template, request

app = Flask(__name__)

THRESHOLD = None
LOCATION = None
HOURS = None


@app.route('/', methods=['GET', 'POST'])
def index():
    THRESHOLD = None
    LOCATION = None
    HOURS = None
    if request.method == 'POST':
        print request.form
        LOCATION = request.form.get('location')
        THRESHOLD = request.form.get('snowfall_threshold')
        HOURS = request.form.get('accumulation_period')
    return render_template("index.html", **{
        'location': LOCATION,
        'snowfall_threshold': THRESHOLD,
        'accumulation_period' : HOURS
    })


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
