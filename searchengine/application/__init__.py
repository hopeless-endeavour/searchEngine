from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# initialise database 
db = SQLAlchemy()

def create_app():

    # initialise Flask app and configure 
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    db.init_app(app)

    # set up app context so the the database can be accessed from within the app
    with app.app_context():
        from . import routes

        # create DB tables
        db.create_all()
        
        return app