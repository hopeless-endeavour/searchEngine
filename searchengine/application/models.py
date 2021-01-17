from . import db

class User(db.Model):

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    password = db.Column(db.String(25), nullable=False)
    img = db.Column(db.String(25), default='default.jpg')

    # articles = db.relationship('Article', secondary='user_article')


class Article(db.Model):

    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    text = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    published = db.Column(db.DateTime)
    url = db.Column(db.String, unique=True, nullable=False)
    cefr = db.Column(db.String, default="Unknown")

    # users = db.relationship('User', secondary='user_article')

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class UserArticle(db.Model):

    __tablename__ = "user_article"
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"))
    article_id = db.Column(db.Integer(), db.ForeignKey("articles.id"))
    db.PrimaryKeyConstraint(user_id, article_id, name='comp_key')