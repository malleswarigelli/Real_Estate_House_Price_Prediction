

from flask import Flask, jsonify, request


app = Flask(__name__)


@app.rout("/", methods = ["GET", "POST"])
def index():
    return "start ML application"

if __name__ == "__main__":
    app.run()
