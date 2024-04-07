from flask import Flask, render_template, redirect, request, abort, make_response, jsonify
from flask_login import LoginManager, current_user, login_required, logout_user

import news_api
import news_resources
from data import db_session
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



@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.rememberme.data)
            return redirect('/')
        return render_template('login.html', message='Nepravilnij login ili parol', form=form)
    return render_template('login.html', title='Avtorizacija', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


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


# @app.route("/session_test")
# def session_test():
#     visit_count = session.get("visit_count", 0)
#     session["visit_count"] = visit_count + 1
#     return make_response(f"Vy prishli {visit_count + 1} raz!")
# @app.route("/cookie_test")
# def cookie_test():
#     visits_count = int(request.cookies.get('visits_test', 0))
#     if visits_count:
#         res = make_response(f"Vi prishli na stranicu {visits_count} raz")
#         res.set_cookie("visits_test", str(visits_count + 1), max_age=60 * 60 * 24 * 365 * 2)
#     else:
#         res = make_response(f"Vi prishli pervij raz za 2 goda")
#         res.set_cookie("visits_test", "1", max_age=60 * 60 * 24 * 365 * 2)
#     return res

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForms()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template("register.html", title="Registration", form=form, message="PAROL NE SOVPADAJET!!!")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template("register.html", title="Registration", form=form,
                                   message="TAKOJ EMEJL UZHE ISPOLZUJETCA!!!")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template("register.html", title="Registration", form=form)


@app.route("/news", methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Dobavlenije novosti', form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == 'GET':
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html', title='Redaktirovanje novosti', form=form)


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


def main():
    db_session.global_init("db/blog_db.sqlite")
    app.register_blueprint(news_api.blueprint)
    api.add_resource(news_resources.NewsListResource, '/api/g2/news')
    api.add_resource(news_resources.NewsResource, '/api/g2/news/<int:news_id>')
    # # user = User()
    # # user.name = 'Gennadij'
    # # user.about = 'about Gennadij'
    # # user.email = 'gennadij@gennadij.com'
    # db_sess = db_session.create_session()
    # # db_sess.add(user)
    # # user = db_sess.query(User)
    # # for user in db_sess.query(User).all():
    # #     print(user.name)
    # # db_sess.commit()
    # #
    # # db_sess = db_session.create_session()
    # # user = db_sess.query(User).filter(User.id == 1).first()
    # # print(user.name)
    # # user.name = 'user name new'
    # # user.created_data = dt.datetime.now()
    # # db_sess.commit()
    # # db_sess.query(User).filter(User.id >= 3).delete()
    # # db_sess.commit()
    #

    # user = db_sess.query(User).filter(User.id == 3).first()
    # news = News(title='Pervaja zapis', content='mnogo mnogo mnogo texta slova bukvi aaaaaaaaaaa', user=user,
    #             is_private=False)
    # user.news.append(news)
    # db_sess.commit()
    app.run()
def abort_if_news_not_found(news_id):
    session = db_session.create_session()
    news = session.query(News).get(news_id)
    if not news:
        abort(404, message=f'News {news_id} not found')

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


if __name__ == '__main__':
    main()
