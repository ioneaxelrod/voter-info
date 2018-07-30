"""User model for Voter Info Project"""

from flask_sqlalchemy import SQLAlchemy
from os import environ
# from model.congressperson import Congressperson
from sqlalchemy.orm.exc import NoResultFound

import requests


REPRESENTATIVE_URL = "https://www.googleapis.com/civicinfo/v2/representatives?key="
CIVIC_KEY = environ['GOOGLE_CIVIC_KEY']

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
        """"""
        with app.app_context():

            search_address = "&address=" + self.address
            request = requests.get(REPRESENTATIVE_URL + CIVIC_KEY + search_address)
            politician_json = request.json()

            politician_info = politician_json['officials']

            congresspeople = []
            for politician in politician_info:
                name_parts = politician['name'].split(" ")
                for part in name_parts:
                    if '.' in part:
                        name_parts.remove(part)
                name = " ".join(name_parts)
                print(name)
                congressperson = Congressperson.query.filter_by(name=name).first()
                if congressperson:
                    congresspeople.append(congressperson)
        return congresspeople






########################################################################################################################
# Main Functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///voteinfo'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)

def create_dummy_user():
    """"""

    user = User(screen_name="ione",
                email="ione@ione.com",
                password=environ["IONE_PASS"],
                address="Stoneridge Dr, Pleasanton, CA, 94588")
    db.session.add(user)
    db.session.commit()


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from controller.server import app

    connect_to_db(app)
    db.create_all()
    user = User.query.get(1)
    print("Connected to DB.")