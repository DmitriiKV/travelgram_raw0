from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired

class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Содержание')
    #file = FileField('Добавить файл')
    category = TextAreaField('Категория')
    is_private = BooleanField('Сделать приватной')
    submit = SubmitField('Сохранить')
