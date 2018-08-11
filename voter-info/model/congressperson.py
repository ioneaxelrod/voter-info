from .db import db
import requests
from .consts import *
from .helpers import parse_vote_from_json

class Congressperson(db.Model):
    """Congressperson for Voter Info Project"""

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


    def get_election_year(self):
        """Getter so just the year is returned, instead of nonsensical month/day
            :return int: year of next election
        """
        return self.next_election.year



    @classmethod
    def get_senators(cls):
        """Gets all congresspeople with the title Senator from database
            :return [Congressperson]: list of Senators
        """

        senators = cls.query.filter(cls.title.like("Senator%")).all()
        return senators

    @classmethod
    def get_representatives(cls):
        """Gets all congresspeople with the title Representative from database
            :return [Congressperson]: list of Representatives
        """

        representatives = cls.query.filter(cls.title == "Representative").all()
        return representatives

    def get_vote_from_roll_call(self, bill):
        """Takes a roll call number from a bill and determines how your congressperson voted on that bill
            :param bill: Bill
            :return str: Congressperson's vote infomration
        """

        if "Representative" in self.title:
            if bill.house_votes_url:
                vote_url = bill.house_votes_url
            else:
                return "No vote information found"
        elif "Senator" in self.title:
            if bill.senate_votes_url:
                vote_url = bill.senate_votes_url
            else:
                return "No vote information found"

        vote_request = requests.get(vote_url, headers={'X-API-Key': PROPUBLICA_KEY})
        vote_json = vote_request.json()
        return parse_vote_from_json(vote_json, self)



