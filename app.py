from flask import Flask

app = Flask("app")

@app.route("/")
def index():
    return "Hello World!"

