from flask import render_template, flash, redirect, url_for, request
from .forms import RecipeURLForm
from app import app
from .scraper import SimplyRecipeScraper
from .cleaner import CommentCleaner
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import pickle
import numpy as np

# note that this is the nlp used throughout this script!
nlp = spacy.load('en_core_web_sm')

#def apply_model(vectorized_reviews, modelfile='app/models/multinomialNB_model1'):
def apply_model(vectorized_reviews, modelfile='app/models/multinomial_nb_model_v2.pkl'):
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

    sorted_indexes = np.argsort(_agg)
    sorted_reviews = []
    for k in sorted_indexes:
        sorted_reviews.append(' '.join([s.text for s in reviews[k]]))

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
    highlighted_sorted_comments = highlight_foods(sorted_comments)
    return render_template('recipe.html',
                            ingredients=ss.ingredient_list,
                            instructions=ss.instructions,
                            sorted_comments=highlighted_sorted_comments,
                            image_url=ss.image_url)

def parse_ingredient_list(ilist):
    ingredients = [s.split('>')[1].split('<')[0] for s in ss.ingredient_list]
    new_ingredients = []
    for ingredient in ingredients:
        ingredient = re.sub("[\d+-/]", "", ' '.join(ingredient)).strip()
        ingredient = ingredient.split(' ')
        
        
def highlight_foods(comments):
    food_lists = ['veggies', 'meats', 'dairy', 'beans', 'condiments', 'fruits', 'breads', 'seafood'] 
    food_corpus = []
    for k in food_lists:
        npz = np.load('app/models/foodlist/{0}.npz'.format(k))
        [food_corpus.append(f.lower()) for f in npz['arr_0'] if len(f) != 0];

    [food_corpus.append(f) for f in ['egg', 'eggs', 'rice', 'pasta', 'quinoa', 'garlic', 'tea', 'oil']];
    food_corpus_lemmat = [f.lemma_ for f in nlp(' '.join(food_corpus))]
    new_comments = []
    for comment in comments:
        new_comment = []
        for c in nlp(comment):
            if c.lemma_ in food_corpus_lemmat and c.lemma_ not in STOP_WORDS :
                new_comment.append('<b class="highlight">{0}</b>'.format(c.text))
            else:
                new_comment.append(c.text)
        new_comments.append(' '.join(new_comment))
    return new_comments
