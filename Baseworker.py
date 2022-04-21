import csv
import os
import sqlite3

from flask import Flask, render_template, request, g, redirect
from flask_login import LoginManager
from flask_login import login_user, current_user
from waitress import serve

from data import db_session
from data.admins import Admin
from data.calls import Calls
from data.goods import Goods
from data.orders import Orders
from data.users import Users
from forms.admin import AdminLoginForm
from forms.good import GoodForm
from forms.user import UserLoginForm
from forms.user_reg import UserRegForm

SECRET_KEY = 'dfbfdbd;.fbdf><dfbdf&3435!@3l'

app = Flask(__name__)
app.config.from_object(__name__)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    if int(user_id) > 0:
        return db_sess.query(Users).get(user_id)
    return db_sess.query(Admin).get(user_id)


@app.route('/')
@app.route('/Главная.html')
def main():
    return render_template('page_1/Главная.html', title='Главная')


@app.route('/Авторизация.html', methods=['GET', 'POST'])
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(Users).filter(Users.email == form.email.data).first()
        admin = db_sess.query(Admin).filter(Admin.email == form.email.data).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin)
            return redirect("/add_good_new_brend")
        elif user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/")
        return render_template('page_1/Авторизация.html', form=form,
                               message="Неправильный логин или пароль")
    print(form.errors)
    return render_template('page_1/Авторизация.html', form=form)


@app.route('/Регистрация.html', methods=['GET', 'POST'])
def register():
    form = UserRegForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        users = db_sess.query(Users).filter(Users.email == form.email.data).first()
        if users:
            return render_template('page_1/Регистрация.html',
                                   message="Пользователь с такой почтой уже существует",
                                   form=form)
        else:
            user = Users()
            user.name = form.name.data
            user.email = form.email.data
            user.password = user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
            use = db_sess.query(Users).filter(Users.email == form.email.data).first()
            login_user(use)
            return redirect("/")
    return render_template('page_1/Регистрация.html', form=form)


@app.route('/О-нас.html')
def about_us():
    return render_template('page_1/О-нас.html', title='О-нас')


@app.route('/Контакты.html', methods=['GET', 'POST'])
def contact():
    form = GoodForm()
    db_sess = db_session.create_session()
    if request.method == 'POST':
        calls_spis = db_sess.query(Calls).all()
        calls = Calls()
        calls.name = request.form.get('name')
        calls.phone = request.form.get('phone')
        calls.message = request.form.get('message')
        calls.is_done = False
        db_sess.add(calls)
        db_sess.commit()
        return render_template('page_1/Контакты.html', form=form,
                               thank_you=f'Спасибо, ваша заявка №{len(calls_spis)}'
                                         f' уже находится в обработке. Мы вам перезвоним')
    elif request.method == 'GET':
        return render_template('page_1/Контакты.html', form=form)


@app.route('/order', methods=['GET', 'POST'])
def order():
    if current_user.is_authenticated:
        form = GoodForm()
        db_sess = db_session.create_session()
        goodses = db_sess.query(Goods).all()
        if request.method == 'POST':
            if request.form.get('Update') == 'Обновить корзину':
                zakaz = {}
                control_sum = 0
                for elem in goodses:
                    zakaz[elem.brend + elem.title] = int(request.form.get(elem.brend + elem.title))
                    control_sum += int(request.form.get(elem.brend + elem.title)) * elem.price
                return render_template('page_1/Заказ.html', form=form, goodses=goodses, zakaz=zakaz,
                                       control_sum=control_sum)
            elif request.form.get('Update') == 'Заказать':
                orders_spis = db_sess.query(Orders).all()
                orders = Orders()
                orders.href = f"static/csv/{len(orders_spis)}.csv"
                db_sess = db_session.create_session()
                user = db_sess.query(Users).filter(Users.id == current_user.get_id()).first()
                orders.email = user.email
                orders.is_done = False
                db_sess.add(orders)
                db_sess.commit()
                with open(orders.href, mode="w", encoding='cp1251', newline='') as f:
                    db_sess = db_session.create_session()
                    goods = db_sess.query(Goods).all()
                    f.truncate()
                    pricewriter = csv.writer(f, delimiter=';')
                    pricewriter.writerow(['id', 'Бренд', 'Название', 'Количество', 'Цена', 'Итог'])
                    control_sum = 0
                    for good in goodses:
                        pricewriter.writerow([good.id, good.brend, good.title,
                                              int(request.form.get(good.brend + good.title)), good.price,
                                              int(request.form.get(good.brend + good.title)) * good.price])
                        control_sum += int(request.form.get(good.brend + good.title)) * good.price
                    pricewriter.writerow(['', '', '', '', '', str(control_sum)])
                f.close()
                zakaz = {}
                control_sum = 0
                for elem in goodses:
                    zakaz[elem.brend + elem.title] = int(request.form.get(elem.brend + elem.title))
                    control_sum += int(request.form.get(elem.brend + elem.title)) * elem.price
                return render_template('page_1/Заказ.html', form=form, goodses=goodses, zakaz=zakaz,
                                       control_sum=control_sum,
                                       thank_you=f'Спасибо за заказ, ваша заявка №{len(orders_spis)}'
                                                 f' уже находится в обработке. На вашу почту придёт письмо')
            else:
                return render_template('page_1/Заказ.html', form=form, goodses=goodses)
        elif request.method == 'GET':
            zakaz = {}
            for elem in goodses:
                zakaz[elem.brend + elem.title] = 0
            return render_template('page_1/Заказ.html', form=form, goodses=goodses, zakaz=zakaz, control_sum=0)
    return redirect('/Авторизация.html')


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
def login_admin():
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
        if current_user.get_id() == '0':
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
        if current_user.get_id() == '0':
            form = GoodForm()
            db_sess = db_session.create_session()
            brends = db_sess.query(Goods.brend).distinct()
            if form.validate_on_submit():
                db_sess = db_session.create_session()
                goodses = db_sess.query(Goods.title).filter(Goods.brend == request.form.get('brend')).distinct()
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


@app.route('/change_product', methods=['GET', 'POST'])
def change_product():
    if current_user.is_authenticated:
        if current_user.get_id() == '0':
            form = GoodForm()
            db_sess = db_session.create_session()
            brends = db_sess.query(Goods.brend).distinct()
            goodseses = db_sess.query(Goods.title).all()
            if form.validate_on_submit():
                db_sess = db_session.create_session()
                goods = db_sess.query(Goods).filter(Goods.brend == request.form.get('brend'),
                                                    Goods.title == request.form.get('title')).first()
                if goods:
                    goods.amount = form.amount.data
                    goods.price = form.price.data
                    db_sess.add(goods)
                    db_sess.commit()
                    return redirect('/change_product')
                else:
                    return render_template('site_admin/Изменить-товар.html', form=form, brends=brends,
                                           goodseses=goodseses, message='Такого товара не существует')
            return render_template('site_admin/Изменить-товар.html', form=form, brends=brends, goodseses=goodseses)
        return redirect('/')
    return redirect('/login_admin')


@app.route('/order_requests', methods=['GET', 'POST'])
def order_requests():
    if current_user.is_authenticated:
        if current_user.get_id() == '0':
            form = AdminLoginForm()
            db_sess = db_session.create_session()
            order_request = db_sess.query(Orders)
            if request.method == 'POST':
                ord = db_sess.query(Orders).filter(Orders.id == int(request.form.get('Update').split('№')[1])).first()
                ord.is_done = True
                db_sess.add(ord)
                db_sess.commit()
                names = db_sess.query(Users).all()
                name = {}
                for elem in names:
                    name[elem.email] = elem.name
                return render_template('site_admin/Заявки-на-заказ.html', form=form,
                                       order_request=order_request, name=name)
            if request.method == 'GET':
                names = db_sess.query(Users).all()
                name = {}
                for elem in names:
                    name[elem.email] = elem.name
                return render_template('site_admin/Заявки-на-заказ.html', form=form,
                                       order_request=order_request, name=name)
        return redirect('/')
    return redirect('/login_admin')


@app.route('/call_requests', methods=['GET', 'POST'])
def call_requests():
    if current_user.is_authenticated:
        if current_user.get_id() == '0':
            form = AdminLoginForm()
            db_sess = db_session.create_session()
            call_request = db_sess.query(Calls)
            if request.method == 'POST':
                ord = db_sess.query(Calls).filter(Calls.id == int(request.form.get('Update').split('№')[1])).first()
                ord.is_done = True
                db_sess.add(ord)
                db_sess.commit()
                return render_template('site_admin/Заявки-на-звонок.html', form=form, call_request=call_request)
            if request.method == 'GET':
                return render_template('site_admin/Заявки-на-звонок.html', form=form, call_request=call_request)
        return redirect('/')
    return redirect('/login_admin')


if __name__ == '__main__':
    db_session.global_init(f"db/goods.db")
    serve(app, host='0.0.0.0', port=5000)
    # app.run(port=5000, host='0.0.0.0')
    
