from flask import Flask, render_template, jsonify, request, make_response, redirect, g, url_for, session
from flask import current_app as app
import json

from application.tfidf.doc_analysis import *
from .models import db, Article, User
# from .forms import QueryForm


@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = User.query.filter_by(username=session['user_id']).first()
        g.user = user


@app.route('/', methods=['post', 'get'])
def index():

    return render_template('index.html')


@app.route('/register', methods=['post', 'get'])
def register():

    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form.get('username')
        password = request.form.get('password')

        print(username, password)

        user_obj = User.query.filter_by(username=username).first()
        if user_obj:
            return "Username taken"
        else:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()

            return redirect(url_for('login'))


    return render_template('register.html')


@app.route('/login', methods=['post', 'get'])
def login():

    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form.get('username')
        password = request.form.get('password')

        user_obj = User.query.filter_by(username=username).first()
        if user_obj:
            session['user_id'] = user_obj.id
            return redirect(url_for('profile'))

        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/profile', methods=['post', 'get'])
def profile():
    # if not g.user:
    #     return redirect(url_for('login'))

    return render_template('profile.html')


@app.route('/logout', methods=['post', 'get'])
def logout():

    session.pop('user_id', None)

    return redirect(url_for('index'))


@app.route('/_background', methods=['post', 'get'])
def background():

    req = request.get_json()
    print(req)

    corpus = readData('application/data')
    results = tf_idf(req['query'], corpus, int(req['n']))

    res = make_response(jsonify(results), 200)

    return res
