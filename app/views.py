from flask import render_template, flash
from app import app

@app.route('/')
@app.route('/index')
def index():
    return render_template('base.html')
    
