from flask import Flask, render_template, jsonify, request, make_response, redirect, url_for, session, flash, g, json, after_this_request
from sqlalchemy import and_
from flask import current_app as app
import random

from .models import db, Article, User, UserArticle
from application.tfidf.tf_idf import Corpus, Query, read_data
from application.tfidf.spider import Spider, TwentyMinSpider

C = Corpus()


def upload_dataset_toDB(path):
    """ Uploads data from dataset from given path into database.  """

    corpus = read_data(path)
    for i in range(len(corpus)):
        add_to_db(Article, title=corpus[i][0], text=corpus[i][1], author=corpus[i][2], published=corpus[i][3], url=corpus[i][4])

    print('Uploaded dataset to DB')


def update_data_file():
    """ Writes data from Corpus to json file. """

    json_data = {"num_docs": C.num_docs, "doc_ids": C.doc_ids,
                 "vocab": C.vocab, "len_vocab": C.len_vocab, "tf_idf": C.tf_idf}

    with open('data_file.json', 'w') as f:
        json.dump(json_data, f)


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


@app.before_first_request
def before_first_request():

    # attempts to open data_file.json that contains Corpus data
    try:
        with open('data_file.json', 'r') as f:
            json_data = json.load(f)
            C.num_docs = json_data["num_docs"]
            C.doc_ids = json_data["doc_ids"]
            C.vocab = json_data["vocab"]
            C.len_vocab = json_data["len_vocab"]
            C.tf_idf = json_data["tf_idf"]

    # if file doesn't exist, upload the dataset to the database, calc tf_idf and update data file
    except FileNotFoundError:
        upload_dataset_toDB("application/data")
        update_tfidf()
        update_data_file()


@app.route('/', methods=['post', 'get'])
def index():

    n_cefrs = {'A1': 0, 'A2': 0, 'B1': 0, 'B2': 0, 'C1': 0, 'C2': 0}
    n_articles = Article.query.count()
    for key, value in n_cefrs.items():
        n_cefrs[key] = Article.query.filter_by(cefr=key).count()

    obj = Article.query.filter_by(id=1).first()
    print("Obj Dict : ", obj.as_dict())
    return render_template('index.html', n_articles=n_articles, n_cefrs=n_cefrs)


@app.route('/register', methods=['post', 'get'])
def register():

    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form.get('username')
        password = request.form.get('password')

        print(username, password)

        user_obj = User.query.filter_by(username=username).first()
        print(user)
        if user_obj:
            flash("Username taken")
            return redirect(url_for('register'))
        else:
            add_to_db(User, username=username, password=password)

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
            if user_obj.password == password:
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


@app.route('/_background', methods=['post', 'get'])
def background():

    req = request.get_json()
    print(req)
    res = []

    if req["domain"] != '' and req['query'] == '':
        article_dict = TwentyMinSpider(
            "https://www.20minutes.fr", int(req['n'])).run()

        print(article_dict.keys())
        # calc cefr
        for i in article_dict:
            article = Article.query.filter_by(url=i).first()
            if not article:
                add_to_db(Article, title=article_dict[i]["title"], text=article_dict[i]["content"],
                          author=article_dict[i]["author"], published=article_dict[i]["published"], url=i)
            else:
                print("Already in DB")

        for i in article_dict.keys():
            doc_obj = Article.query.filter_by(url=i).first()
            doc = doc_obj.as_dict()
            doc['text'] = doc['text'][:197]
            res.append(doc)

        @after_this_request
        def update(response):
            print("yoik")
            update_tfidf()
            update_data_file()
            print("Successfully updated")
            return response
            
        


    else:
        doc_ids = C.search_query(req['query'])[:int(req['n'])]
        
        for i in doc_ids:
            doc_obj = Article.query.filter_by(id=i).first()
            doc = doc_obj.as_dict()
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
