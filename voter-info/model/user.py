"""User model for Voter Info Project"""

from flask_sqlalchemy import SQLAlchemy
from os import environ
import requests

db = SQLAlchemy()

##############################################################################
# User definition

class User(db.Model):
    """User for Voter Info Project"""

    ___tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    screen_name = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String, nullable=True)


    def __repr__(self):
        return f'<user_id={self.user_id}, address={self.address}>'

    def find_representatives(self):
        representative_url = "https://www.googleapis.com/civicinfo/v2/representatives?key="
        civic_key = environ['GOOGLE_CIVIC_KEY']
        search_address = "&address=" + self.address

        request = requests.get(representative_url + civic_key + search_address)
        politician_json = request.json()



def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///voteinfo'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from controller.server import app
    connect_to_db(app)
    print("Connected to DB.")