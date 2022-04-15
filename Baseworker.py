import os
import sqlite3
import csv
from flask import Flask, render_template, request, g, flash, redirect
from flask_login import LoginManager
from flask_login import login_user, current_user
from werkzeug.security import generate_password_hash

from HelpBase import HelpBase
from data import db_session
from data.admins import Admin
from data.goods import Goods
from forms.admin import AdminLoginForm
from forms.good import GoodForm

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
    return db_sess.query(Admin).get(user_id)


@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = HelpBase(db)


@app.route('/')
@app.route('/Главная.html')
def main():
    return render_template('page_1/Главная.html', title='Главная')


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


@app.route('/price_list')
def price_list():
    with open("static/csv/price.csv", mode="w", encoding='cp1251', newline='') as f:
        db_sess = db_session.create_session()
        goods = db_sess.query(Goods).all()
        f.truncate()
        pricewriter = csv.writer(f, delimiter=';')
        pricewriter.writerow(['id', 'Бренд', 'Название', 'Количество', 'Цена'])
        for good in goods:
            pricewriter.writerow([good.id, good.brend, good.title, good.amount, good.price])
    f.close()
    return render_template('page_1/Скачать-прайс.html', title='Скачать-прайс')


@app.route('/login_admin', methods=['GET', 'POST'])
def login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        admin = db_sess.query(Admin).filter(Admin.email == form.email.data).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin)
            return redirect("/add_good_new_brend")
        return render_template('site_admin/Авторизация.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('site_admin/Авторизация.html', form=form)


@app.route('/add_good_new_brend', methods=['GET', 'POST'])
def add_good_new_brand():
    if current_user.is_authenticated:
        if current_user.get_id() == 1:
            form = GoodForm()
            if form.validate_on_submit():
                db_sess = db_session.create_session()
                goods = Goods()
                goods.brend = form.brend.data
                goods.title = form.title.data
                goods.amount = form.amount.data
                goods.price = form.price.data
                db_sess.add(goods)
                db_sess.commit()
                return redirect('/add_good_new_brend')
            return render_template('site_admin/Новый-бренд.html', form=form)
        return redirect('/')
    return redirect('/login_admin')


@app.route('/add_good_old_brend', methods=['GET', 'POST'])
def add_good_old_brand():
    if current_user.is_authenticated:
        if current_user.get_id() == 1:
            form = GoodForm()
            db_sess = db_session.create_session()
            brends = db_sess.query(Goods.brend).distinct()
            if form.validate_on_submit():
                db_sess = db_session.create_session()
                goodses = db_sess.query(Goods.title).distinct()
                if (form.title.data,) in goodses:
                    goods = db_sess.query(Goods).filter(Goods.title == form.title.data).first()
                    goods.amount += form.amount.data
                    goods.price = form.price.data
                    db_sess.add(goods)
                    db_sess.commit()
                else:
                    goods = Goods()
                    goods.brend = request.form.get('brend')
                    goods.title = form.title.data
                    goods.amount = form.amount.data
                    goods.price = form.price.data
                    db_sess.add(goods)
                    db_sess.commit()
                return redirect('/add_good_old_brend')
            return render_template('site_admin/Добавить-товар.html', form=form, brends=brends)
        return redirect('/')
    return redirect('/login_admin')


if __name__ == '__main__':
    db_session.global_init(f"db/goods.db")
    app.run(port=8080, host='127.0.0.1')
