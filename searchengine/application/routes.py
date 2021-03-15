import random
import pickle
import time 
import os 
import datetime
import requests
from multiprocessing import Pool

from flask import Flask, render_template, jsonify, request, make_response, redirect, url_for, session, flash, g, json, after_this_request
from flaskthreads import AppContextThread 
from sqlalchemy import func, case, text
from flask import current_app as app
from passlib.hash import sha256_crypt

from .models import db, Article, User, UserArticle
from application.python_scripts.tf_idf import Corpus, Query
from application.python_scripts.spider import TwentyMinSpider, FigaroSpider, FranceInfoSpider
from application.python_scripts.cefr_calculator import CefrCalculator

C = Corpus()
cefr_calc = CefrCalculator()

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
            if ("anibis.ch" not in json_obj['url']) and ("yahoo" not in json_obj['url']) and ("dealabs" not in json_obj['url']) and (len(json_obj["text"]) > 500): # or (check_url(json_obj['url']))
                data.append([json_obj['title'], json_obj['text'], json_obj['author'], datetime.datetime.strptime(
                    json_obj['published'][:10], "%Y-%m-%d"), json_obj['url'], json_obj["thread"]["site"]])
                

    return data


def upload_dataset_toDB(path):
    """ Uploads data from dataset from given path into database.  """

    corpus = read_data(path)
    for i in range(len(corpus)):
        cefr = cefr_calc.cefr_score(corpus[i][1])
        # print(cefr)
        add_to_db(Article, title=corpus[i][0], text=corpus[i][1], author=corpus[i][2], published=corpus[i][3], url=corpus[i][4], domain=corpus[i][5], cefr=cefr)

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

    C = Corpus()
    articles = Article.query.all()
    for i in articles:
        C.add_document(i.id, i.title, i.text, True)

    C.calc_tfidf()
    print("TF-IDF updated.")
    return C

def start_crawl(domain, n):
    res = []

    # create appropriate spider for chosen domain and run
    if domain == "20min":
        article_dict = TwentyMinSpider().run(n)
    elif domain == "figaro":
        article_dict = FigaroSpider().run(n)
    elif domain == "franceinfo":
        article_dict = FranceInfoSpider().run(n)

    # flag var is to indicate whether any new articles, in which case the TF-IDF values would need updating 
    flag = False
    for i in article_dict:
        # if article is not already in the DB add it
        article = Article.query.filter_by(url=i).first()
        if not article:
            flag = True
            cefr = cefr_calc.cefr_score(article_dict[i]["content"])
            # print(cefr)
            add_to_db(Article, title=article_dict[i]["title"], text=article_dict[i]["content"],
                        author=article_dict[i]["author"], published=article_dict[i]["published"] if article_dict[i]['published'] else None, url=i, cefr=cefr)
        else:
            print(f"{article} already in DB.")

    # filter to get all articles just scrapped 
    article_objs = Article.query.filter(Article.url.in_(article_dict.keys())).all()

    return article_objs, flag

def apply_filters(req):
    ordering = []
    article_objs = Article.query

    if req["query"]:
        # submit the user query to the Corpus 
        doc_ids = C.submit_query(req['query'])
        query_filter = {}
        for i in range(len(doc_ids)):
            query_filter[doc_ids[i]] = i

        # sort articles so that documents calculated to be similiar by the Corpus are first 
        article_objs = article_objs.order_by((case(query_filter, value=Article.id, else_=len(doc_ids)+1)))

    if req['level']:
        # create case statement for the CEFR level 
        cefr_filter = case({req['level']: "0"}, value=Article.cefr, else_="1")
        ordering.append(cefr_filter)

    if req['author']:
        # create case statement for the author filter 
        author_filter = case({req['author']: "0"}, value=Article.domain, else_="1")
        ordering.append(author_filter)  

    if req["filter_type"]:
        # order articles appropriatly according to the date published filter 
        if req["filter_type"] == "newest":
            date_filter = Article.published.desc()
        elif req["filter_type"] == "oldest":
            date_filter = Article.published.asc()
        ordering.append(date_filter)
    
    
    if ordering:
        # apply all case filters from above 
        article_objs = article_objs.order_by(*ordering)

    return article_objs.all()

def update():
    global C
    print("update started...")
    start = time.perf_counter()
    C = update_tfidf()
    update_data_file()
    finish = time.perf_counter()
    print(f"Successfully updated in {round(finish-start,2)} second(s)")   


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


@app.route('/', methods=['get', 'post'])
def index():

    n_cefrs = {'A1': 0, 'A2': 0, 'B1': 0, 'B2': 0, 'C1': 0, 'C2': 0, "Unknown": 0}
    # gets all distinct authors in the db
    authors = [i[0] for i in db.session.query(Article.author).order_by(Article.author).distinct().all()] 
    # gets number of articles in the db
    n_articles = Article.query.count() 
    # get domains 
    domains = [i[0] for i in db.session.query(Article.domain).order_by(Article.domain).distinct().all()] 
    # get how many articles have each level of cefr
    cefrs = db.session.query(func.count(Article.id), Article.cefr).group_by(Article.cefr).all()
    for count, cefr in cefrs: 
        if cefr in n_cefrs:
            n_cefrs[cefr] = count 
    

    return render_template('index.html', n_articles=n_articles, n_cefrs=n_cefrs, authors=authors, domains=domains)


@app.route('/register', methods=['post', 'get'])
def register():

    if request.method == 'POST':
        # ensures no user is in the session 
        session.pop('user_id', None)

        # get form information 
        username = request.form.get('username')
        password = request.form.get('password')

        # check if username is already taken
        user_obj = User.query.filter_by(username=username).first()
        if user_obj:
            flash("Username taken")
        elif len(password) < 8 or not any(i.isdigit() for i in password):
            flash("Password must be at least 8 characters long and contain at least one number.")
        else:
            add_to_db(User, username=username, password=sha256_crypt.hash(password)) # hash user's password 
            
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['post', 'get'])
def login():

    if request.method == 'POST':
        # ensures no user is already in the session 
        session.pop('user_id', None)

        # get form information
        username = request.form.get('username')
        password = request.form.get('password')

        # checks if userrname exists in the users table 
        user_obj = User.query.filter_by(username=username).first()
        if user_obj:
            # verify password hashes are the same 
            if sha256_crypt.verify(password, user_obj.password):
                # add user to the session 
                session['user_id'] = user_obj.id
                print(session)
                return redirect(url_for('bookmarks'))
            else:
                flash("Password is incorrect")
        else:
            flash("User does not exist")

    return render_template('login.html')


@app.route('/bookmarks', methods=['post', 'get'])
def bookmarks():
    
    # if there is user in the session find their bookmarks from the DB, otherwise redirect to login
    if session.get('user_id', None) :
        user_id = session['user_id']
        print(session)
        user = User.query.filter_by(id=user_id).first()
        bookmarks = db.session.query(Article).join(UserArticle).join(User).filter(User.id == user_id).all()
        return render_template('bookmarks.html', user=user, bookmarks=bookmarks)
    else:
        flash("No username found in session")
        return redirect(url_for("login"))


@app.route('/view_article/<article_id>', methods=['post', 'get'])
def view_article(article_id):
    
    # get appropriate article from DB using article id passed into the route url
    article = Article.query.filter_by(id=article_id).first()
    print(article.published)
    return render_template('view_article.html', article=article, article_id=int(article_id))


@app.route('/logout', methods=['post', 'get'])
def logout():

    # remove user from session 
    session.pop('user_id', None)
    flash("Logged Out")

    return redirect(url_for('index'))
      

@app.route('/_background', methods=['post'])
def background():
    
    # recieve query 
    req = request.get_json()
    print(req)
    res = []

    if req["type"] == "current":
        # if user selected to get current news start crawling news from specified domain
        article_objs, flag = start_crawl(req["domain"], int(req["n"]))
        if flag: 
            # if there are new articles, then TF-IDF needs updating, start thread for update() 
            thread = AppContextThread(target=update).start()
        
    else:
        # query the database option chosen, so apply filters 
        article_objs = apply_filters(req)

    # return only the specified number of articles 
    for i in article_objs[:int(req['n'])]:
        doc = i.as_dict()
        doc['text'] = doc['text'][:197] # only take first few characters as a summary 
        res.append(doc)

    #return response to js front end 
    return make_response(jsonify(res, 200))


@app.route('/_bookmark', methods=['get', 'post'])
def bookmark_page():

    # receive request from js front end 
    req = request.get_json()
    print('Request: ', req)
    print('User_id: ', req['user_id'])

    user_id = req['user_id']
    article_id = req["article_id"]

    # if the type of request is "bookmark" add record to user_article table 
    if req["type"] == "bookmark":
        try:
            add_to_db(UserArticle, article_id=article_id, user_id=user_id)
            res = make_response(jsonify({"message": "Successfully bookmarked"}), 200)
        except:
            res = make_response(
                jsonify({"message": "Already bookmarked"}), 200)

    # if the type is "unbookmark" delete appropriate record from user_article table
    else:
        try:
            bookmark = UserArticle.query.filter_by(
                user_id=user_id, article_id=article_id).first()
            db.session.delete(bookmark)
            db.session.commit()
            res = make_response(jsonify({"message": "Successfully unbookmarked"}), 200)
        except Exception as e:
            print(e.message, e.args)
            res = make_response(jsonify({"message": "Error: {e.message}" }), 500)

    return res
