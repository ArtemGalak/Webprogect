from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class GoodForm(FlaskForm):
    brand = StringField('Brand', validators=[DataRequired()])
    title = StringField('Good_title', validators=[DataRequired()])
    amount = IntegerField('Amount', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    submit = SubmitField('Submit')