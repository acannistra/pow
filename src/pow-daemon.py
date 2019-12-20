from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return("here")


if __name__ == "__main__":
    Flask.run(app)
