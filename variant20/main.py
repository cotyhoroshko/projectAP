from flask import Flask


def run_foo(test: bool = True):
    app = Flask(__name__)

    @app.route('/')
    def hello():
        return 'Вітаю Вас!'

    @app.route('/api/v1/hello-world-20')
    def hello_world_20():
        return 'Hello World 20'

    return app