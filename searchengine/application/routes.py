from flask import Flask, render_template, jsonify, request, make_response
from flask import current_app as app
import json

from application.tfidf.doc_analysis import *
from .models import db, Article
from .forms import QueryForm


@app.route('/', methods=['post', 'get'])
def index():

    return render_template('index.html')

@app.route('/_background', methods=['post', 'get'])
def background():

    req = request.get_json()
    print(req)

    # corpus = readData('application/data')
    # results = tf_idf(query, corpus)

    res = make_response(jsonify(req), 200)

    return res
