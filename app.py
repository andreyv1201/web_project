@login_manager.user_loader
def load_user(id):
    return db.session.query(UserModel).get(id)


@app.route("/")
def MainForAnon():
    if current_user.is_authenticated:
        return redirect(url_for("MainPage"))
    return render_template("main_anon.html")


@app.route("/main/", methods=['get','post'])
@login_required
def MainPage():
	AllUsers = db.session.query(UserModel).all()
	return render_template("main_page.html", all = AllUsers)


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
def Chat():
    TimeData = []
    data = db.session.query(MessagesModel).order_by(-MessagesModel.id_message)
    for i in data:
        ID = i.id_message
        if i.send_to_str:
            Time = str(i.send_to_str)
            TimeConv1 = Time.split()[1]
            TimeConv2 = Time.split()[0]
            TimeHour = TimeConv1.split(".")[0]
            TimeData.append({'id': ID, 'timeHour': TimeHour, 'timeDay': TimeConv2[:10]})

    print(TimeData)

    form = ChatForm()

    if form.validate_on_submit():
        nick = current_user.nick
        message = form.message.data
        add_message = MessagesModel(message=message, user_nick=nick)
        db.session.add(add_message)
        db.session.commit()
        return redirect(url_for("Chat"))

    return render_template("chat.html", form=form, data=data, TimeData=TimeData)


@app.route("/registration/", methods=['POST', 'GET'])
def Reg():
    if current_user.is_authenticated:
        return redirect(url_for("MainPage"))

    form = UserForm()
    All = db.session.query(UserModel.nick).all()
    all_users = []

    for i in All:
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

    All = db.session.query(UserModel.nick).all()
    all_nicks = []

    for i in All:
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


@app.route("/logout_user/")
def LogOut():
	logout_user()
	return redirect("/login")

@app.errorhandler(401)
def NotAuthorised(error):
	return render_template("NotAuthorised.html")


@app.errorhandler(404)
def NotFound(error):
	return render_template("error404.html")