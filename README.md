h1 лабораторна робота №1 Варіант 20

* Клонувати репозиторій
```

git clone https://github.com/cotyhoroshko/projectAP.git

```

* Інсталювати віртуальне середовище
```
pip install pipenv
```

* Запустити віртуальне середовище
```
pipenv shell
```

* Встановити залежності
```
pipenv install --dev
```

* Запустити сервер
```

sudo gunicorn -w 4 "variant20.main:run_foo()"

```

* Перевірити роботу сервера

<http://127.0.0.1:5000/api/v1/hello-world-20>

{
        "email": "m@l.ua",
        "name": "Maks",
        "password_hash": "1234"
}

{
        "description": "Doing different course works on different subjects related to chemistry",
        "id": 1,
        "modifier": "public",
        "summary": "Doing course works",
        "topic": "study",
        "user_id": 1
}


















@app.route('/sign-in', methods=['GET'])
@auth.login_required
def sign_in():

    # email = request.args.get('email')
    # password = request.args.get('password')
    user = auth.current_user()
    if user == "Unauthorized":
        return "You do not have sufficient editing rights", 403
    email = auth.current_user().email
    password = auth.current_user().password_hash

    user = session.query(User).filter(User.email == email).first()
    if user is None:
        return "Email not found", 400

    if not bcrypt.checkpw(password.encode('utf8'), user.password_hash.encode('utf8')):
        return "Wrong password", 400
    t = auth.current_user()
    app.logger.info(t)

    app.logger.info(t)

    return jsonify(UserSchema().dump(user)), 200


@app.route('/logout')
@auth.login_required
def logout():
    auth.current_user().logout_user()
    return 'Logout', 401
