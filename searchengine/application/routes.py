import random
import pickle
import time 
import os 
import datetime
import requests

from flask import Flask, render_template, jsonify, request, make_response, redirect, url_for, session, flash, g, json, after_this_request
from flaskthreads import AppContextThread 
from flask import current_app as app
from passlib.hash import sha256_crypt

from .models import db, Article, User, UserArticle
from application.python_scripts.tf_idf import Corpus, Query
from application.python_scripts.spider import TwentyMinSpider, FigaroSpider, FranceInfoSpider

C = Corpus()

def read_data(path):
    """ Reads the json data from the dataset in the given directory. Returns 2D array of data """

    def check_url(url):
        req = requests.head(url)
        if req.status_code != 200:
            print(f'Error. Status code: {req.status_code}')
            return False
        else:
            return True

    data = []

    for i in os.listdir(path=path):
        with open(f'{path}/{i}', 'r', encoding="utf8") as f:
            full_data = f.read()
            json_obj = json.loads(full_data)

            # only append to data array if there is content in the "text" field and the article isn't from anibis ( an irrelevant website )
            if ("anibis.ch" not in json_obj['url']) and (json_obj["text"] != ''): # or (check_url(json_obj['url']))
                data.append([json_obj['title'], json_obj['text'], json_obj['author'], datetime.datetime.strptime(
                    json_obj['published'][:10], "%Y-%m-%d"), json_obj['url']])


    return data


def upload_dataset_toDB(path):
    """ Uploads data from dataset from given path into database.  """

    corpus = read_data(path)
    for i in range(len(corpus)):
        add_to_db(Article, title=corpus[i][0], text=corpus[i][1], author=corpus[i][2], published=corpus[i][3], url=corpus[i][4])

    print('Uploaded dataset to DB.')


def update_data_file():
    """ Writes data from Corpus to pickle. """

    data = {"num_docs": C.num_docs, "doc_ids": C.doc_ids,
                 "vocab": C.vocab, "len_vocab": C.len_vocab, "tf_idf": C.tf_idf}

    with open('data_file.pkl', 'wb') as f:
        pickle.dump(data, f)

    print("Data file updated.")


def add_to_db(model_obj, **kwargs):

    record = model_obj(**kwargs)
    db.session.add(record)
    db.session.commit()


def update_tfidf():

    global C
    C = Corpus()
    articles = Article.query.all()
    for i in articles:
        C.add_document(i.id, i.title, i.text, True)

    C.calc_tfidf()
    print("TF-IDF updated.")


@app.before_first_request
def before_first_request():

    if not db.session.query(Article).first():
        print('Empty DB.')
        upload_dataset_toDB("application/data")
        
    # attempts to open data_file.pkl that contains Corpus data
    try:
        with open('data_file.pkl', 'rb') as f:
            data = pickle.load(f)
            C.num_docs = data["num_docs"]
            C.doc_ids = data["doc_ids"]
            C.vocab = data["vocab"]
            C.len_vocab = data["len_vocab"]
            C.tf_idf = data["tf_idf"]

    # if file doesn't exist, upload the dataset to the database, calc tf_idf and update data file
    except FileNotFoundError:
        print("File not found.")
        update_tfidf()
        update_data_file()


@app.route('/', methods=['post', 'get'])
def index():

    n_cefrs = {'A1': 0, 'A2': 0, 'B1': 0, 'B2': 0, 'C1': 0, 'C2': 0, "Unknown": 0}
    authors = [i[0] for i in db.session.query(Article.author).order_by(Article.author).distinct().all()] # gets all the authors in the db
    n_articles = Article.query.count() # gets number of articles in the db

    for key, value in n_cefrs.items():
        n_cefrs[key] = Article.query.filter_by(cefr=key).count()

    return render_template('index.html', n_articles=n_articles, n_cefrs=n_cefrs, authors=authors)


@app.route('/register', methods=['post', 'get'])
def register():

    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form.get('username')
        password = request.form.get('password')

        user_obj = User.query.filter_by(username=username).first()
        print(user_obj)
        if user_obj:
            flash("Username taken")
            return redirect(url_for('register'))
        else:
            add_to_db(User, username=username, password=sha256_crypt.hash(password))

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
            if sha256_crypt.verify(password, user_obj.password):
                session['user_id'] = user_obj.id
                print(session)
                return redirect(url_for('profile'))
            else:
                flash("Password is incorrect")
        else:
            flash("User does not exist")

    return render_template('login.html')


@app.route('/profile', methods=['post', 'get'])
def profile():

    if session.get('user_id', None) is not None:
        user_id = session['user_id']
        print(session)
        user = User.query.filter_by(id=user_id).first()
        ua = UserArticle.query.filter_by(user_id=user_id).all()
        bookmarks = []
        for i in ua:
            bookmarks.append(Article.query.filter_by(id=i.article_id).first())
        print(bookmarks)
        return render_template('profile.html', user=user, bookmarks=bookmarks)
    else:
        flash("No username found in session")
        return redirect(url_for("login"))


@app.route('/view_article/<article_id>', methods=['post', 'get'])
def view_article(article_id):

    article = Article.query.filter_by(id=article_id).first()
    return render_template('view_article.html', article=article, article_id=int(article_id))


@app.route('/logout', methods=['post', 'get'])
def logout():

    session.pop('user_id', None)
    flash("Logged Out")

    return redirect(url_for('index'))


@app.route('/_upload', methods=['POST', 'GET'])
def upload():

    # TODO: set max image upload size
    if request.method == 'POST':
        user_id = session['user_id']
        print(user_id)
        user = User.query.filter_by(id=user_id).first()
        f = request.files['file']
        print(f)
        filename = f'{user_id}{os.path.splitext(f.filename)[1]}'
        user.img = filename
        print(user.img)
        db.session.add(user)
        db.session.commit()
        f.save(f"/application/static/img/{filename}")
        print(filename)

        return redirect(url_for('profile'))

    if request.method == 'GET':
        if session.get('user_id'):
            img = f"static/img/{User.query.filter_by(id=session['user_id']).first().img}"
        else:
            img = 'static/img/default.jpg'

        return make_response(jsonify(img), 200)


@app.route('/_background', methods=['post'])
def background():
    def update():

            print("update started...")
            start = time.perf_counter()
            update_tfidf()
            update_data_file()
            finish = time.perf_counter()
            print(f"Successfully updated in {round(finish-start,2)} second(s)")

    req = request.get_json()
    print(req)
    res = []

    if req["domain"] != '' and req['query'] == '':
        if req["domain"] == "20min":
            article_dict = TwentyMinSpider().run(int(req['n']))
        elif req["domain"] == "figaro":
            article_dict = FigaroSpider().run(int(req['n']))
        elif req["domain"] == "franceinfo":
            article_dict = FranceInfoSpider().run(int(req['n']))

        print(article_dict.keys())
        # calc cefr
        for i in article_dict:
            article = Article.query.filter_by(url=i).first()
            if not article:
                add_to_db(Article, title=article_dict[i]["title"], text=article_dict[i]["content"],
                          author=article_dict[i]["author"], published=article_dict[i]["published"] if article_dict[i]['published'] else None, url=i)
            else:
                print(f"{article} already in DB.")

        article_objs = Article.query.filter(Article.url.in_(article_dict.keys())).all()
        print("Article_objs: ", article_objs)
        for i in article_objs:
            doc = i.as_dict()
            doc['text'] = doc['text'][:197]
            res.append(doc)

        thread = AppContextThread(target=update).start()
            
    else:
        doc_ids = C.submit_query(req['query'])
        if req["filter_type"] == "newest":
            article_objs = Article.query.filter(Article.id.in_(doc_ids)).order_by(Article.published.desc()).all()
        elif req["filter_type"] == "oldest":
            article_objs = Article.query.filter(Article.id.in_(doc_ids)).order_by(Article.published.asc()).all()
        else:
            article_objs = Article.query.filter(Article.id.in_(doc_ids)).all()
        
        print("articles by cefr: ", Article.query.filter(Article.cefr=="A1").all())


        for i in article_objs[:int(req['n'])]:
            doc = i.as_dict()
            doc['text'] = doc['text'][:197]
            res.append(doc)

    return make_response(jsonify(res, 200))


@app.route('/_bookmark', methods=['get', 'post'])
def bookmarkPage():

    req = request.get_json()
    print('Request: ', req)
    print('User_id: ', req['user_id'])

    user_id = req['user_id']
    article_id = req["article_id"]

    if req["type"] == "bookmark":
        try:
            add_to_db(UserArticle, article_id=article_id, user_id=user_id)
            res = make_response(jsonify({"message": "bookmarked"}), 200)
        except:
            res = make_response(
                jsonify({"message": "already bookmarked"}), 200)
    else:
        try:
            bookmark = UserArticle.query.filter_by(
                user_id=user_id, article_id=article_id).first()
            db.session.delete(bookmark)
            db.session.commit()
            res = make_response(jsonify({"message": "unbookmarked"}), 200)
        except Exception as e:
            print(e.message, e.args)
            res = make_response(jsonify({"message": "not ok"}), 500)

    return res
