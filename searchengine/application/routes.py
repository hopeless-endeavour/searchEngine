from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask import current_app as app

from .models import db, Article
from .forms import QueryForm


@app.route('/')
def index():

    return render_template('index.html')
