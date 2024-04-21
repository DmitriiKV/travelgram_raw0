from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


# класс для формы авторизации
class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    rememberme = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")
