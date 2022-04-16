from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class GoodForm(FlaskForm):
    brend = StringField('Бренд', validators=[DataRequired()])
    title = StringField('Название товара', validators=[DataRequired()])
    amount = IntegerField('Количество товара', validators=[DataRequired()])
    price = IntegerField('Цена', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')