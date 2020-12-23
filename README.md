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