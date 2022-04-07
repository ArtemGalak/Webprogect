import sqlite3
import os
from flask import Flask, render_template, request, g, flash, abort, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from HelpBase import HelpBase

DATABASE = 'Base.db'
SECRET_KEY = 'dfbfdbd;.fbdf><dfbdf&3435!@3l'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'Base.db')))


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None


@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = HelpBase(db)


@app.route('/')
@app.route('/Главная.html')
def main():
    return render_template('index.html', title='Главная')


@app.route('/Авторизация.html', methods=['GET', 'POST'])
def reqister():
    if request.method == "POST":
        if len(request.form['name']) > 3 and '@' in request.form['email'] \
                and len(request.form['text']):
            hash = generate_password_hash((request.form['text']))
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash("Вы успешно зарегестрировались!", "seccess")
                return redirect(url_for('Главная.html'))
    return render_template('Авторизация.html', title='Регистрация')


@app.route('/О-нас.html')
def about_us():
    return render_template('О-нас.html', title='О-нас')


@app.route('/Контакты.html')
def contact():
    return render_template('Контакты.html', title='Контакты')


@app.route('/Скачать-прайс.html')
def price():
    return render_template('Скачать-прайс.html', title='Скачать-прайс')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
