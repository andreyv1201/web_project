from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.news import NewsForm
from forms.user import RegisterForm, LoginForm
from data.news import News
from data.users import User
from data import db_session
from logging import error
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, PasswordField
from wtforms.validators import Email, DataRequired, Length
import sqlite3


class ChatForm(FlaskForm):
    message = TextAreaField("Текст сообщения", validators=[DataRequired()])
    submit = SubmitField("Отправить сообщение")


app = Flask(__name__)
# 2. Затем сразу после создания приложения flask инициализируем LoginManager:
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


# 3. Для верной работы flask-login у нас должна быть
# функция load_user для получения пользователя
# украшенная декоратором login_manager.user_loader. Добавим ее:
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

# 4. Кроме того, наша модель для пользователей
# должна содержать ряд методов
# для корректной работы flask-login,
# но мы не будем создавать их руками,
# а воспользуемся множественным наследованием.
# см. файл: \data\users.py

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/blogs.db")
    app.run(port=8080, host='127.0.0.1')


@app.route("/")
def index():
    db_sess = db_session.create_session()
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/all_users")
@login_required
def all_users():
    con = sqlite3.connect("blogs.sqlite")
    cur = con.cursor()
    user = cur.execute("""SELECT n  ame FROM users""").fetchall()
    return render_template("all_users.html", user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Не забудьте импортировать класс LoginForm и метод login_user из модуля flask-login.
    form = LoginForm()
    # Если форма логина прошла валидацию,
    if form.validate_on_submit():
        # Создаем сессию для работы БД:
        db_sess = db_session.create_session()
        # Находим в БД пользователя по введенной почте:
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        # Проверяем, введен ли для него правильный пароль, если да, вызываем функцию login_user модуля flask-login
        if user and user.check_password(form.password.data):
            #  и передаем туда объект нашего пользователя, а также значение галочки «Запомнить меня»:
            login_user(user, remember=form.remember_me.data)
            # После чего перенаправляем пользователя на главную страницу нашего приложения:
            return redirect("/")
        # Если пароль неправильный:
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    # Если авторизация не пройдена, то возвращаемся на начало авторизации:
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    TimeData = []
    form = ChatForm()
    return render_template("chat.html", form=form, data=[], TimeData=TimeData)


@app.route("/logout_user/")
def LogOut():
    logout_user()
    return redirect("/login")


@app.errorhandler(401)
def NotAuthorised(error):
    return render_template("NotLogin.html")


@app.errorhandler(404)
def NotFound(error):
    return render_template("error404.html")



if __name__ == '__main__':
    main()