from flask import render_template, flash, redirect, url_for, request
from .forms import RecipeURLForm
from app import app
from .scraper import SimplyRecipeScraper

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = RecipeURLForm()
    if form.validate_on_submit():
        url = str(form.name.data)
        return redirect(url_for('recipe', data=url))
    return render_template('index.html',
                           title='Find a Recomendation!',
                           form=form)
    
@app.route('/recipe', methods=['GET'])
def recipe():
    recipeurl = request.args.get('data')
    ss = SimplyRecipeScraper(recipeurl) 
    print(ss.ingredient_list)
    print(ss.instructions)
    return render_template('recipe.html',
                            ingredients=ss.ingredient_list,
                            instructions=ss.instructions
                          )
