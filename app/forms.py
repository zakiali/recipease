from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class RecipeURLForm(FlaskForm):
    name = StringField('url', validators=[DataRequired()], default='https://www.simplyrecipes.com/recipes/african_chicken_peanut_stew/')
    submit = SubmitField('Go!')

