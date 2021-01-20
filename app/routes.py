from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.j2', title='Home')
