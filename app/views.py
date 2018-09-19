from flask import render_template, flash, redirect, url_for
from .forms import RecipeURLForm
from app import app

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = RecipeURLForm()
    if form.validate_on_submit():
        url = str(form.name.data)
        return redirect(url_for('recipe'))
    return render_template('index.html',
                           title='Find a Recomendation!',
                           form=form)
    
@app.route('/recipe', methods=['GET'])
def recipe():
    return render_template('recipe.html')
