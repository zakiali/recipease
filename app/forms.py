from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, DateField
from wtforms.validators import DataRequired

class RecipeURL(FlaskForm):
    url = StringField('url', validators=[DataRequired()])

