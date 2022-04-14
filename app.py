@login_manager.user_loader
def load_user(id):
    return db.session.query(UserModel).get(id)


@app.route("/")
def MainForAnon():
    if current_user.is_authenticated:
        return redirect(url_for("MainPage"))
    return render_template("main_anon.html")


@app.route("/info_user/<int:id>")
@login_required
def infoUserId(id):
    user = db.session.query(UserModel).get(id)
    str1 = str(user.created_on)

    date1 = str1.split()[0]
    date2 = date1.split("-")
    year = date2[0]
    month = date2[1]
    day = date2[2]

    time1 = str1.split()[1]
    time2 = time1.split(":")

    date = {'year': year, 'month': month, 'day': day}
    hour = time2[0]
    minute = time2[1]
    second = time2[2].split(".")[0]
    time = {'hour': hour, 'minute': minute, 'second': second}

    return render_template("info_user_id.html", user=user, date=date, time=time)


@app.route("/main/", methods=['get', 'post'])
@login_required
def MainPage():
    allusers = db.session.query(UserModel).all()
    return render_template("main_page.html", all=allusers)


@app.route("/update_acc/<int:id>/", methods=["POST", "GET"])
@login_required
def UpdateAcc(id):
    form = UpdateForm()
    all = db.session.query(UserModel.nick).all()
    this_user = db.session.query(UserModel).get(id)

    if form.validate_on_submit():
        if current_user.id == id:
            all_nicks = []
            for i in all:
                for j in i:
                    if current_user.nick != j:
                        all_nicks.append(j)

            new_nick = form.upd_nick.data
            new_pass = form.upd_password.data

            if new_nick:
                if form.upd_nick.data not in all_nicks:
                    if len(new_nick) >= 4:
                        if len(new_nick) <= 16:
                            this_user.nick = new_nick
                            db.session.commit()
                            flash("Ник обновлен")
                        else:
                            flash("Слишком длинный ник - (максимум 16 символов)")
                    else:
                        flash("Слишком маленький ник - (минимум 4 символа)")
                else:
                    flash("Пользователь с таким ником уже существует!")

            if new_pass:
                if len(form.upd_password.data) >= 4:
                    if len(form.upd_password.data) <= 50:
                        this_user.set_password(form.upd_password.data)
                        db.session.commit()
                        flash("Пароль обновлен")
                    else:
                        flash("Слишком длинный пароль - (максимум 50 символов)")
                else:
                    flash("Слишком короткий пароль - (минимум 4 символов)")

        else:
            flash("Ты хочешь изменить данные другого аккаунта!")

    return render_template("upd_acc.html", form=form)


@app.route("/delete_acc/<int:id>/")
@login_required
def DeleteAcc(id):
    this_user = db.session.query(UserModel).get(id)

    if current_user.id == id:
        try:
            db.session.delete(this_user)
            db.session.commit()
            flash("Аккаунт успешно удален")
        except:
            flash("Произошла ошибка удаления аккаунта!")
    else:
        flash("Ты пытаешься удалить не свой аккаунт!")

    return render_template("del_acc.html")


@app.route("/chat/", methods=["GET", "POST"])
@login_required
def chat():
    datatime = []
    data = db.session.query(MessagesModel).order_by(-MessagesModel.id_message)
    for i in data:
        ID = i.id_message
        if i.send_to_str:
            time = str(i.send_to_str)
            time1 = time.split()[1]
            time2 = time.split()[0]
            hour = time1.split(".")[0]
            datatime.append({'id': ID, 'timeHour': hour, 'timeDay': time2[:10]})

    form = ChatForm()

    if form.validate_on_submit():
        nick = current_user.nick
        message = form.message.data
        add_message = MessagesModel(message=message, user_nick=nick)
        db.session.add(add_message)
        db.session.commit()
        return redirect(url_for("chat"))

    return render_template("chat.html", form=form, data=data, TimeData=datatime)


@app.route("/registration/", methods=['POST', 'GET'])
def Reg():
    if current_user.is_authenticated:
        return redirect(url_for("MainPage"))

    form = UserForm()
    all = db.session.query(UserModel.nick).all()
    all_users = []

    for i in all:
        for j in i:
            all_users.append(j.lower())

    if form.validate_on_submit():
        nick = form.nick.data
        password = form.password.data

        if nick.lower() not in all_users:
            add_user_db = UserModel(nick=nick, password=password)
            db.session.add(add_user_db)
            add_user_db.set_password(password)
            db.session.commit()
            return redirect(url_for('Login'))
        else:
            flash("Такой аккаунт уже существует, авторизируйся")
            return redirect(url_for('Login'))

    return render_template("registration.html", form=form)


@app.route("/login/", methods=["POST", "GET"])
def Login():
    form = LoginForm()

    if current_user.is_authenticated:
        return redirect(url_for("MainPage"))

    all = db.session.query(UserModel.nick).all()
    all_nicks = []

    for i in all:
        for j in i:
            all_nicks.append(j.lower())

    if form.validate_on_submit():
        if form.check_nick.data.lower() in all_nicks:
            user = db.session.query(UserModel).filter(UserModel.nick == form.check_nick.data).first()
            if user and user.check_password(form.check_pass.data):
                login_user(user)
                return redirect(url_for("MainPage"))
        else:
            flash("Такой пользователь не зарегистрирован!")

    return render_template("login.html", form=form)