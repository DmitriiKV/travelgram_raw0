from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class NewsForm(FlaskForm):
    title = StringField('Zagolovok', validators=[DataRequired()])
    content = TextAreaField('Soderjanije')
    is_private = BooleanField('Privatnaja')
    submit = SubmitField('Sohranit')
