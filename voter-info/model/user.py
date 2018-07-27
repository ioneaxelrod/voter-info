"""User model for Voter Info Project"""

from flask_sqlalchemy import SQLAlchemy
from os import environ
import requests

db = SQLAlchemy()

##############################################################################
# User definition

class User(db.Model):
    """User for Voter Info Project"""

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



##############################################################################
# Politician definition

class CongressPerson(db.Model):
    """Politician for Voter Info Project"""

    congress_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    title = db.Column(db.String(64), nullable=False)
    next_election = db.Column(db.Datetime)
    party = db.Column(db.String(32), nullable=False)
    address = db.Column(db.String)
    phone_number = db.String(db.String(10))
    twitter = db.String(db.String(64))
    facebook = db.String(db.String(64))
    youtube =db.String(db.String(64))

    @classmethod
    def retrieve_politicians_from_json(cls, json):
        office_info = json['offices']
        politician_info = json['officials']

        # Retrieve info about politician title from office info,
        # place in dictionary for easy retrieval
        office_dict = {}
        politician_list = []

        for office in office_info:
            title = office['name']
            official_index = office['officialIndices']
            for index in official_index:
                office_dict[index] = title;


        for i in range(len(politician_info)):

            title = office_dict[i]
            name = politician_info[i]['name']
            address = politician_info[i]['address']
            political_party = politician_info[i]['party']

            politician = Politician(politician_title=title,
                                    politician_name=name,
                                    political_party=political_party,
                                    address=address
                                    )
            politician_list.append(politician)

        return politician_list

##############################################################################
# Politician definition

class Bill:
    """Politician for Voter Info Project"""

    def __init__(self, bill_id, ):




##############################################################################
# Helper functions


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