from flask import render_template, flash, redirect, url_for, request
from .forms import RecipeURLForm
from app import app
from .scraper import SimplyRecipeScraper
from .cleaner import CommentCleaner
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import pickle
import numpy as np

DEFAULT_URL = 'https://www.simplyrecipes.com/recipes/african_chicken_peanut_stew/'
SAVE = False

# note that this is the nlp used throughout this script!
# nlp = spacy.load('en_core_web_sm')
nlp = spacy.load('en')


def check_input(text_string):
    if ( ('simplyrecipes' in text_string) or 
            (text_string.startswith('http://')) or
            (text_string.startswith('https://')) or
            ('simplyrecipes.com/recipes' in text_string) ):
        return True
    else:
        return False


def sanitize(text_string):
    if text_string.startswith('www.'):
        return 'https://' + text_string
    else:
        return text_string
    

#def apply_model(vectorized_reviews, modelfile='app/models/multinomialNB_model1'):
def apply_model(vectorized_reviews, modelfile='app/models/random_forest_model_v3.pkl'):
#def apply_model(vectorized_reviews, modelfile='app/models/random_forest_model_v2.pkl'):
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

    for i, k in enumerate(sorted_reviews):
        pop_list = []
        if len(k) < 5:
            pop_list.append(i)
    for k in pop_list:
        sorted_reviews.append(sorted_reviews.pop(k))

    return sorted_reviews


def remove_questions(sorted_comments):
    move_to_end_of_list = []
    for i, comm in enumerate(sorted_comments):
        if comm.strip().endswith('?'):
            move_to_end_of_list.append(sorted_comments.pop(i))

    for k in move_to_end_of_list:
        sorted_comments.append(k)

    return sorted_comments
            
    
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = RecipeURLForm()
    if form.validate_on_submit():
        url = str(form.name.data)
        if check_input(url):
            url = sanitize(url)
            return redirect(url_for('recipe', data=url))
        else:
            return render_template('error.html')
    return render_template('index.html',
                           title='Find a Recomendation!',
                           form=form)


@app.route('/prez')
def view_presentation():
    return render_template('prez.html', title='Demo Presentation')

    
@app.route('/recipe', methods=['GET'])
def recipe():
    recipeurl = request.args.get('data')
    if recipeurl == DEFAULT_URL and not SAVE:
        dd = pickle.load(open('app/models/default_data.pkl', 'rb'))
        return render_template('recipe.html',
                               ingredients=dd['ingredients'],
                               title=dd['title'],
                               instructions=dd['instructions'],
                               sorted_comments=dd['comments'],
                               image_url=dd['image_url'])
    else:
        try:
            ss = SimplyRecipeScraper(recipeurl) 
            cc = CommentCleaner(ss.comments)
            predictions = apply_model(cc.all_vectorized_reviews)
            sorted_comments = sort_comments(predictions, cc.all_reviews)
            sorted_comments = remove_questions(sorted_comments)
            highlighted_sorted_comments = highlight_foods(sorted_comments)
            if recipeurl == DEFAULT_URL and SAVE:
                default_dict = {}
                default_dict['ingredients'] = ss.ingredient_list
                default_dict['title'] = ss.title
                default_dict['instructions'] = ss.instructions
                default_dict['image_url'] = ss.image_url
                default_dict['comments'] = highlighted_sorted_comments
                pickle.dump(default_dict, open('app/models/default_data.pkl', 'wb'))
        except IndexError:
            return render_template('tryagain.html')
            
        return render_template('recipe.html',
                                ingredients=ss.ingredient_list,
                                title=ss.title,
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
        for f in npz['arr_0']:
            if len(f) != 0:
                food_corpus.append(f.lower())

    for f in ['egg', 'eggs', 'rice', 'pasta', 'quinoa', 'garlic', 'tea', 'oil']:
        food_corpus.append(f)
    food_corpus_lemmat = [f.lemma_ for f in nlp(' '.join(food_corpus)) if f.pos_ != 'PUNC']
    remove_these_foods_from_lemmat = [')', '(', 'half', 'flavor', '8', '.', '-', '/', '&', 'white', 'red', 'de', 'cup', 'grate', 'black']
    for f in remove_these_foods_from_lemmat:
        while f in food_corpus_lemmat:
            food_corpus_lemmat.remove(f)

    for f in food_corpus_lemmat:
        if not f.isalpha():
            while f in food_corpus_lemmat:
                food_corpus_lemmat.remove(f)

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
