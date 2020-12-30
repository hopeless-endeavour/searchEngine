from flask import Flask, render_template, jsonify, request, make_response, redirect, url_for, session, flash, g
from sqlalchemy import and_
from flask import current_app as app
import json

from .models import db, Article, User, UserArticle
from application.tfidf.tf_idf import Corpus, Query, read_data
from application.tfidf.spider import Spider

C = Corpus()

@app.before_first_request
def before_first_request():
    # data = read_data(('application/data'))
    # articles = Article.query.all()
    # for i in articles:
    #     C.add_document(i.id, i.title, i.text, False)
    
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
    
    print(C.num_docs)

    # C.calc_tfidf()
    # print(C.len_vocab)
    # print(C.df_vec)
    # res = C.search_query("macron")
    
    # json_data = {"num_docs": C.num_docs, "doc_ids": C.doc_ids, "vocab": C.vocab, "len_vocab": C.len_vocab, "tf_matrix": C.tf_matrix, "df_vec": C.df_vec, "idf_vec": C.idf_vec, "tf_idf": C.tf_idf}
    
    # with open('data_file.json', 'w') as f:
    #     json.dump(json_data, f)  


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
            flash("Username taken")
            return redirect(url_for('register'))
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
        return render_template('profile.html', user=user)
    else:
        flash("No username found in session")
        return redirect(url_for("login"))


@app.route('/viewArticle', methods=['post', 'get'])
def viewArticle():

    article = Article.query.filter_by(id=25).first()
    return render_template('viewArticle.html', article=article)
    

@app.route('/logout', methods=['post', 'get'])
def logout():

    session.pop('user_id', None)
    flash("Logged Out")

    return redirect(url_for('index'))


@app.route('/_upload', methods=['post', 'get'])
def upload():

    #TODO: set max image upload size 
    if request.method == 'POST':
        user_id = session['user_id']
        user = User.query.filter_by(id=user_id).first()
        f = request.files['file']  
        filename = f'{user_id}{os.path.splitext(f.filename)[1]}'
        user.img = filename
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

    if req["domain"] != None: 
        # search domain 
        # render results 
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
            doc['url'] = doc_obj.url
            res.append(doc)


        res = make_response(jsonify(res, 200))

    return res

@app.route('/_bookmark', methods = ['get', 'post'])
def bookmarkPage():

    req = request.get_json()
    print(req)
    print(session)
    if session.get('user_id', None) is not None:
        user_id = session['user_id']
        print(user_id)
        article_id = Article.query.filter_by(id=req["id"])

        if req["type"] == "bookmark":
            bookmark = UserArticle(user_id=user_id, article_id=article_id)
            db.session.add(bookmark)
            db.session.commit()
            res = make_response(jsonify({"message": "OK"}), 200)
        else:
            try:
                bookmark = UserArticle.query.filter_by(UserArticle.user_id==user_id, UserArticle.article_id==article_id).first()
                db.session.delete(bookmark)
                db.session.commit()   
                res = make_response(jsonify({"message": "OK"}), 200)
            except:
                print('error')
                res = make_response(jsonify({"message": "not ok"}), 500)
     
        return res 
    else:
        flash("No username found in session")
        return redirect(url_for('login'))


@app.route('/uploadtoDB')
def uploadtoDB():

    corpus = readData('application/data')
    for i in range(len(corpus)): 
        article = Article(title=corpus[i][0], text=corpus[i][1], author=corpus[i][2], published=corpus[i][3], url=corpus[i][4])
        db.session.add(article)
    
    flash('success')
    db.session.commit()  
    
    return redirect(url_for('index'))    