import os

import requests
from flask import Flask, render_template, redirect, request, abort, make_response, jsonify
from flask_login import LoginManager, current_user, login_required, logout_user

import news_api
import news_resources
from data import db_session
from data.category import Category
from data.user import User
from data.news import News
from forms.LoginForm import LoginForm
from flask_login import login_user
from flask_restful import reqparse, abort, Api, Resource

import datetime as dt

from forms.news import NewsForm
from forms.user import RegisterForms

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'sekret_key_aaaaaaa'
app.config['PERMANENT_SESSION_LIFETIME'] = dt.timedelta(days=240)
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# обработчик адреса, отображающего карту города, указанного пользователем
@app.route('/cities/<city>', methods=['GET', 'POST'])
def show_city(city):
    geocoder_request = f'http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={city}&format=json'
    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()
        toponym = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
        toponym_address = toponym['metaDataProperty']['GeocoderMetaData']['text']
        height, width = toponym['Point']['pos'].split()
    map_request = f"http://static-maps.yandex.ru/1.x/?ll={height},{width}&spn=0.1,0.1&l=map"
    return redirect(map_request)


# функция для получения пользователя
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# обработчик адреса /login
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.rememberme.data)
            return redirect('/')
        return render_template('login.html', message='Неправильный логин или пароль', form=form)
    return render_template('login.html', title='Авторизация', form=form)


# обработчик адреса /are_you_logout
@app.route("/are_you_logout")
@login_required
def are_you_logout():
    return render_template('are_you_logout.html')


# обработчик адреса /logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


# обработчик адреса, отображающего посты одной категории
@app.route("/<string:category_str>", methods=['GET', 'POST'])
def category(category_str):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.category == category_str)
    return render_template("index.html", news=news, current_user=current_user)


# обработчик адреса главной страницы
@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True)
        )
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news, current_user=current_user)


# обработчик адреса /register
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForms()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template("register.html", title="Регистрация", form=form, message="Пароль не совпадает")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template("register.html", title="Регистрация", form=form,
                                   message="Такой email уже используется")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template("register.html", title="Регистрация", form=form)


# обработчик адреса /news для добавления новости
@app.route("/news", methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        category = Category()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        news.city = form.city.data
        category.name = form.category.data
        news.category = form.category.data
        news.categories.append(category)
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление поста', form=form)


# обработчик адреса страницы для загрузки фото
@app.route('/file/<int:id>')
def file(id):
    return render_template('image_render.html', item_id=id)


# обработчик адреса страницы для загрузки фото
@app.route('/upload/<int:id>', methods=['POST'])
@login_required
def upload_file(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()
    if 'file' not in request.files:
        news.img = ''
        return redirect('/')
    file = request.files['file']
    if file.filename == '':
        news.img = ''
        return redirect('/')
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
    if news:
        news.img = file.filename
    db_sess.commit()
    return redirect('/')


# обработчик адреса для редактирования новости
@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == 'GET':
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()
        category = db_sess.query(News).filter(News.id == id, News.user == current_user).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
            form.city.data = news.city
            form.category.data = news.category
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()
        category = Category()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            news.city = form.city.data
            news.category = form.category.data
            category.name = form.category.data
            news.categories.append(category)
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html', title='Редактирование поста', form=form)


# обработчик адреса для удаления новости
@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


# основная функция приложения
def main():
    db_session.global_init("db/blog_db.sqlite")
    app.register_blueprint(news_api.blueprint)
    api.add_resource(news_resources.NewsListResource, '/api/g2/news')
    api.add_resource(news_resources.NewsResource, '/api/g2/news/<int:news_id>')
    app.run()


# функция для обработки ошибки 404
def abort_if_news_not_found(news_id):
    session = db_session.create_session()
    news = session.query(News).get(news_id)
    if not news:
        abort(404, message=f'News {news_id} not found')


# функция для обработки ошибки 400
@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


if __name__ == '__main__':
    main()
