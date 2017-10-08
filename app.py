from flask import Flask, request, json
from celery import Celery
import time


app = Flask(__name__)

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'], broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract=True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

app.config.update(
    CELERY_RESULT_BACKEND='redis://localhost:6379/0',
    CELERY_BROKER_URL='redis://localhost:6379/0'
)

celery = make_celery(app)

@celery.task()
def keep_adding(num_start, num_to_add, addition_list=[]):
    seconds = 10
    if len(addition_list) >= seconds:
        return addition_list

    time.sleep(1)
    result = num_start + num_to_add
    addition_list.append(result)
    print(result)
    keep_adding(result, num_to_add, addition_list)

@app.route('/')
def home():
    print(request)
    return "hello"

