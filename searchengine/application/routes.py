from flask import Flask, render_template, jsonify, request, make_response, redirect, url_for, session, flash, g, json
from sqlalchemy import and_
from flask import current_app as app

from .models import db, Article, User, UserArticle
from application.tfidf.tf_idf import Corpus, Query, read_data
from application.tfidf.spider import Spider

C = Corpus()


def upload_dataset(path):
    """ Uploads data from dataset from given path into database.  """

    corpus = read_data(path)
    for i in range(len(corpus)):
        article = Article(title=corpus[i][0], text=corpus[i][1],
                          author=corpus[i][2], published=corpus[i][3], url=corpus[i][4])
        db.session.add(article)

    db.session.commit()
    print('success')


def update_data_file():
    """ Writes data from Corpus to json file. """

    json_data = {"num_docs": C.num_docs, "doc_ids": C.doc_ids, "vocab": C.vocab, "len_vocab": C.len_vocab,
                 "tf_matrix": C.tf_matrix, "df_vec": C.df_vec, "idf_vec": C.idf_vec, "tf_idf": C.tf_idf}

    with open('data_file.json', 'w') as f:
        json.dump(json_data, f)


def add_to_db(model_obj, **kwargs):

    # add_to_db(User, username="bob", password="bob")
    record = model_obj(**kwargs)
    db.session.add(record)
    db.session.commit()


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
            C.tf_matrix = json_data["tf_matrix"]
            C.df_vec = json_data["df_vec"]
            C.idf_vec = json_data["idf_vec"]
            C.tf_idf = json_data["tf_idf"]

    # if file doesn't exist, upload the dataset to the database and do corpus calculations
    except FileNotFoundError:
        upload_dataset("appplication/data")
        articles = Article.query.all()
        for i in articles:
            C.add_document(i.id, i.title, i.text, True)

        C.calc_tfidf()
        update_data_file()

    # print(C.len_vocab)
    # print(C.df_vec)
    # res = C.search_query("macron")


@app.route('/', methods=['post', 'get'])
def index():

    n_cefrs = {'A1': 0, 'A2': 0, 'B1': 0, 'B2': 0, 'C1': 0, 'C2': 0}
    # a = db.session.execute('select count(id) as article_id from articles').scalar()
    # print("num", a)
    n_articles = Article.query.count()
    for key, value in n_cefrs.items():
        n_cefrs[key] = Article.query.filter_by(cefr=key).count()

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

    if req["domain"] != '':
        spider = Spider(
            "https://www.20minutes.fr/gastronomie/2940355-20201230-remede-cuites-hot-shot-huitres-armand-arnal", int(req['n']))
        article_dict = spider.run()
        C.add_document(103, article_dict["https://www.20minutes.fr/gastronomie/2940355-20201230-remede-cuites-hot-shot-huitres-armand-arnal"]['title'],
                       article_dict["https://www.20minutes.fr/gastronomie/2940355-20201230-remede-cuites-hot-shot-huitres-armand-arnal"]['content'], False)
        print(C.documents)
        # calc cefr
        # add to corpus
        # update tfidf
        pass

    else:
        doc_ids = C.search_query(req['query'])[:int(req['n'])]
        res = []
        for i in doc_ids:
            doc = {}
            doc_obj = Article.query.filter_by(id=i).first()
            doc['id'] = doc_obj.id
            doc['title'] = doc_obj.title
            doc['text'] = doc_obj.text[:197]
            doc['cefr'] = doc_obj.cefr
            doc['url'] = doc_obj.url
            res.append(doc)

        res = make_response(jsonify(res, 200))

    return res


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
