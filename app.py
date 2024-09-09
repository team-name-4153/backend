
from flask import Flask
import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('settings.py')
    return app

app = create_app()

@app.route('/')
def hello_world():
    return 'Hello World'

if __name__ == '__main__':
    
    app.run(debug=app.config["DEBUG"])