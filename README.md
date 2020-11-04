/api/v1/hello-world-20
export FLASK_APP="main:run_foo"
sudo apt install gunicorn
sudo gunicorn -w 4 "main:run_foo()"
sudo gunicorn -w 4 --reload "main:run_foo()"
sudo gunicorn -w 4 --reload -b localhost:5000 "main:run_foo()"
gunicorn main:run_foo
