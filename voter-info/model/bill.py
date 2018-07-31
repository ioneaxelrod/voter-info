from flask_sqlalchemy import SQLAlchemy
from os import environ
import requests

db = SQLAlchemy()
BILL_BY_CATEGORY_URL= "https://api.propublica.org/congress/v1/bills/subjects/{subject}.json"
PROPUBLICA_KEY = environ['PROPUBLICA_CONGRESS_KEY']


########################################################################################################################
# Category definition

class Bill(db.Model):
    """"""

    __tablename__ = "bills"

    bill_id = db.Column(db.String, unique=True, nullable=False, primary_key=True)
    bill_title = db.Column(db.String(64), unique=True, nullable=False)
    bill_uri = db.Column(db.String, unique=True, nullable=False)
    summary = db.Column(db.String, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)

    category = db.relationship("Category", backref=db.backref("categories", order_by=category_id))



    @classmethod
    def retrieve_bills_by_category(cls, category):
        search_url = BILL_BY_CATEGORY_URL.replace("{subject}", category)
        fill_bill_request = requests.get(search_url, headers={'X-API-Key': PROPUBLICA_KEY})
        bill_json = fill_bill_request.json()
        parse_bills_from_json(bill_json, category)


########################################################################################################################
# Helper Functions

def parse_bills_from_json(json, category):
    """"""

    bills = json["results"]

    for bill in bills:
        bill_id = bill['bill_id']
        bill_title = bill['title']
        bill_uri = bill['bill_uri']
        summary = bill['summary']
        category_id = category.category_id

        bill = Bill(bill_id=bill_id, bill_title=bill_title, bill_uri=bill_uri, summary=summary, category_id=category_id)

        db.session.add(bill)

    db.session.commit()


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

    from server import app
    from model.category import Category

    connect_to_db(app)
    db.create_all()
    sexual_health = Category(name="sexual-health")
    db.session.add(sexual_health)
    db.session.commit()
    Bill.retrieve_bills_by_category(sexual_health)
    print("Connected to DB.")
