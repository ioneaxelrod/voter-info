from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime
from controller.server import app

import requests

db = SQLAlchemy()
HOUSE_URL = "https://api.propublica.org/congress/v1/115/house/members.json"
SENATE_URL = "https://api.propublica.org/congress/v1/115/senate/members.json"
PROPUBLICA_KEY = environ['PROPUBLICA_CONGRESS_KEY']


class Congressperson(db.Model):
    """"""

    __tablename__ = "congresspeople"

    congress_id = db.Column(db.String, unique=True, nullable=False, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    title = db.Column(db.String(32), nullable=False)
    party = db.Column(db.String(32), nullable=False)
    phone = db.Column(db.String(20))
    next_election = db.Column(db.DateTime)
    twitter = db.Column(db.String(64))
    facebook = db.Column(db.String(64))
    youtube = db.Column(db.String(64))


########################################################################################################################
# Helper Functions

def load_congresspeople_into_db():
    """"""


    # load senators
    fill_senate_request = requests.get(SENATE_URL, headers={'X-API-Key': PROPUBLICA_KEY})
    senate_json = fill_senate_request.json()
    parse_member_from_json(senate_json)

    # load representatives
    fill_house_request = requests.get(HOUSE_URL, headers={'X-API-Key': PROPUBLICA_KEY})
    house_json = fill_house_request.json()
    parse_member_from_json(house_json)


def parse_member_from_json(json):
    """"""

    members = json["results"][0]['members']

    for member in members:
        if member['in_office'] == 'false':
            print("skip")
        else:
            congress_id = member['id']
            name = parse_name(member['first_name'], member['last_name'])
            title = member['title']
            party = member['party']
            phone = member['phone']
            next_election = parse_year(member['next_election'])
            twitter = member['twitter_account']
            facebook = member['facebook_account']
            youtube = member['youtube_account']

            congressperson = Congressperson(congress_id=congress_id,
                                            name=name,
                                            title=title,
                                            party=party,
                                            phone=phone,
                                            next_election=next_election,
                                            twitter=twitter,
                                            facebook=facebook,
                                            youtube=youtube
                                            )

            db.session.add(congressperson)
            db.session.commit()


def parse_name(first_name, last_name):
    """"""

    return first_name + " " + last_name


def parse_year(year):
    """"""

    return datetime.strptime(year, '%Y')


########################################################################################################################
# Main Functions

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

    connect_to_db(app)
    db.create_all()
    load_congresspeople_into_db()
    print("Connected to DB.")