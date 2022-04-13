import sqlite3
import os
from flask import Flask, render_template, request, g, flash, abort, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from HelpBase import HelpBase
from data import db_session
from forms.good import GoodForm
from data.forms import Goods
from flask_login import LoginManager
from flask_login import login_user
from flask_login import login_required
from flask_login import current_user
from flask_login import logout_user

DATABASE = 'Base.db'
SECRET_KEY = 'dfbfdbd;.fbdf><dfbdf&3435!@3l'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'Base.db')))
login_manager = LoginManager()
login_manager.init_app(app)



def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = HelpBase(db)


@app.route('/')
@app.route('/Главная.html')
def main():
    return render_template('page_1/index.html', title='Главная')


@app.route('/Авторизация.html', methods=['GET', 'POST'])
def reqister():
    if request.method == "POST":
        if len(request.form['name']) > 3 and '@' in request.form['email'] \
                and len(request.form['text']):
            hash = generate_password_hash((request.form['text']))
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            print(res)
            if res:
                flash("Вы успешно зарегестрировались!", "seccess")
                return redirect('/Главная.html')
    return render_template('/page_1/Авторизация.html', title='Регистрация')


@app.route('/О-нас.html')
def about_us():
    return render_template('page_1/О-нас.html', title='О-нас')


@app.route('/Контакты.html')
def contact():
    return render_template('page_1/Контакты.html', title='Контакты')


@app.route('/Скачать-прайс.html')
def price():
    return render_template('page_1/Скачать-прайс.html', title='Скачать-прайс')


@app.route('/add_good_new_brend',  methods=['GET', 'POST'])
def add_good_new_brand():
    form = GoodForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        goods = Goods()
        goods.title = form.title.data
        goods.amount = form.amount.data
        goods.price = form.price.data
        current_user.jobs.append(jobs)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('Добавить-товар.html', form=form)


if __name__ == '__main__':
    db_session.global_init(f"db/blogs.db")
    app.run(port=8080, host='127.0.0.1')
