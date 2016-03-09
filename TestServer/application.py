from flask import Flask
from flask import render_template


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/mod')
def modindex():
    source = render_template('index.html')
    return source.replace('This is a template', 'This iis a template').replace('Bootstrap', 'Boo0ststrap')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
