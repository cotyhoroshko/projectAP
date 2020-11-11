h1 лабораторна робота №1 Варіант 20

* Клонувати репозиторій
```
git clonehttps://github.com/cotyhoroshko/projectAP.git
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
gunicorn variant20.main:run_foo
```

* Перевірити роботу сервера

<http://127.0.0.1:5000/api/v1/hello-world-20>
