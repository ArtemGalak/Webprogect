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


@app.route('/', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
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


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
