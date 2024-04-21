from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FileField, SelectField
from wtforms.validators import DataRequired


# класс для формы новостей
class NewsForm(FlaskForm):
    CHOICES = ['еда', 'достопримечательности', 'проживание']
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Содержание')
    city = StringField('Город', validators=[DataRequired()])
    category = StringField('Категории', validators=[DataRequired()])
    is_private = BooleanField('Сделать приватной')
    submit = SubmitField('Сохранить')
