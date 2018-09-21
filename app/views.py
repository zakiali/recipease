from flask import render_template, flash, redirect, url_for, request
from .forms import RecipeURLForm
from app import app
from .scraper import SimplyRecipeScraper
from .cleaner import CommentCleaner
import pickle
from numpy import argsort

def apply_model(vectorized_reviews, modelfile='models/multinomialNB_model1'):
    '''
    Applies the pickled sklearn model to the scraped reviews.
    Args:
        vectorized_reviews (dict): dictionarry of vectorized comments.
            for each key, there is a sparse matrix for each of the comments.
        modelfile (str): path for the pickled sklearn model file
    '''
    model = pickle.load(open(modelfile, 'rb'))
    predictions_per_comment = {}
    for k,v in vectorized_reviews.items():
        predictions_per_comment[k] = model.predict_proba(v)
        
    return predictions_per_comment


def sort_comments(predictions, reviews):
    '''
    Sort the comments based on the predicted probablities.

    Args:
        predictions (dict): Dictionary of the predictions 
        reviews (dict): Dictionary of all the reviews (must have same 
            keys as the predictions.)
    '''
    aggregated_predictions = {}
    for k, v in predictions.items():
        aggregated_predictions[k] = np.average(v, axis=0)
    
    _agg = []
    for k in sorted(aggregated_predictions):
        _agg.append(aggregated_predictions[k][0])

    sorted_indexes = argsort(_agg)
    sorted_reviews = []
    for k in sorted_indexes:
        sorted_reviews.append(reviews[k])

    return sorted_reviews


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
    cc = CommentCleaner(ss.comments)
    predictions = apply_model(cc.all_vectorized_reviews)
    sorted_comments = sort_comments(predictions, cc.all_reviews)
    return render_template('recipe.html',
                            ingredients=ss.ingredient_list,
                            instructions=ss.instructions
                            sorted_comments=sorted_comments
                          )
