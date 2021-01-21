import os 

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__)))

class Config():
    SECRET_KEY = 'P~-\xcek\xc0\xb5\xa9o7\xc6\x96eR\xfeVs\xdf\xdf\x8b\xad\xbb\xd50'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///"+os.path.join(basedir, "database.db")

