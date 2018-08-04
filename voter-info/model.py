from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
import requests

HOUSE_URL = "https://api.propublica.org/congress/v1/115/house/members.json"
SENATE_URL = "https://api.propublica.org/congress/v1/115/senate/members.json"
BILL_BY_CATEGORY_URL= "https://api.propublica.org/congress/v1/bills/subjects/{subject}.json"
REPRESENTATIVE_URL = "https://www.googleapis.com/civicinfo/v2/representatives?key="

PROPUBLICA_KEY = environ['PROPUBLICA_CONGRESS_KEY']
CIVIC_KEY = environ['GOOGLE_CIVIC_KEY']

db = SQLAlchemy()

########################################################################################################################
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
        # with app.app_context():

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

    def add_user_categories(self, categories):
        added_categories = []
        for category in categories:
            added_categories.append(UserCategory(user_id=self.user_id, category_id=category.category_id))
        db.session.add_all(added_categories)
        db.session.commit()


# Helper Functions

def create_dummy_user():
    """"""

    user = User(screen_name="ione",
                email="ione@ione.com",
                password=environ["IONE_PASS"],
                address="Stoneridge Dr, Pleasanton, CA, 94588")
    db.session.add(user)
    db.session.commit()

########################################################################################################################
# Category definition

class Category(db.Model):
    """"""

    __tablename__ = "categories"

    category_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)



# Helper Functions

def load_categories_into_db():
    with open("subjects.txt") as file:
        categories = []
        for line in file:
            categories.append(Category(name=line))

        db.session.add_all(categories)
        db.session.commit()



########################################################################################################################
# Congressperson definition

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

    def get_election_year(self):
        return self.next_election.year



    @classmethod
    def get_senators(cls):
        senators = cls.query.filter(cls.title.like("Senator%")).all()
        return senators

    @classmethod
    def get_representatives(cls):
        representatives = cls.query.filter(cls.title == "Representative").all()
        return representatives


# Helper Functions

def load_congresspeople_into_db():
    """"""


    # load senators
    fill_senate_request = requests.get(SENATE_URL, headers={'X-API-Key': PROPUBLICA_KEY})
    senate_json = fill_senate_request.json()
    parse_members_from_json(senate_json)

    # load representatives
    fill_house_request = requests.get(HOUSE_URL, headers={'X-API-Key': PROPUBLICA_KEY})
    house_json = fill_house_request.json()
    parse_members_from_json(house_json)


def parse_members_from_json(json):
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
# Bill definition

class Bill(db.Model):
    """"""

    __tablename__ = "bills"

    bill_id = db.Column(db.String,
                        unique=True,
                        nullable=False,
                        primary_key=True)
    bill_title = db.Column(db.String, nullable=False)
    bill_uri = db.Column(db.String, unique=True, nullable=False)
    summary = db.Column(db.String)

    @classmethod
    def retrieve_bills_by_category(cls, category):
        """"""

        subject = format_category_name(category)
        search_url = BILL_BY_CATEGORY_URL.replace("{subject}", subject)
        print(search_url)
        fill_bill_request = requests.get(search_url, headers={'X-API-Key': PROPUBLICA_KEY})
        print(fill_bill_request.text)
        bill_json = fill_bill_request.json()

        parse_bills_from_json(bill_json, category)


# Helper Functions

def format_category_name(category):
    """"""

    category_words = category.name.rstrip().replace(',', '').split(" ")
    return "-".join(category_words)

def parse_bills_from_json(json, category):
    """"""
    if json.get('error'):
        print("No results found")
        return
    bills = json["results"]

    for bill in bills:
        bill_id = bill['bill_id']
        bill_title = bill['short_title']
        bill_uri = bill['bill_uri']
        summary = bill['summary']

        bill = Bill(bill_id=bill_id,
                    bill_title=bill_title,
                    bill_uri=bill_uri,
                    summary=summary,
                    )
        bill_category = BillCategory(bill_id=bill_id, category_id=category.category_id)
        db.session.add(bill_category)
        db.session.add(bill)



    db.session.commit()

########################################################################################################################
# UserCategory definition

class UserCategory(db.Model):
    """"""

    __tablename__ = "user_categories"

    user_category_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey(Category.category_id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.user_id))

    category = db.relationship("Category", backref="user_categories")
    user = db.relationship("User", backref="user_categories")


########################################################################################################################
# BillCategory definition

class BillCategory(db.Model):
    """"""

    __tablename__ = "bill_categories"

    bill_category_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    category_id = db.Column(db.Integer)

    category_id = db.Column(db.Integer, db.ForeignKey(Category.category_id))
    bill_id = db.Column(db.String, db.ForeignKey(Bill.bill_id))

    category = db.relationship("Category", backref="bill_categories")
    bill = db.relationship("Bill", backref="bill_categories")


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

    connect_to_db(app)
    db.drop_all()
    db.create_all()

    print("Connected to DB.")
    print("\n\n\n=============================================")


    # Create User
    create_dummy_user()
    user = User.query.get(1)
    print(user)
    print("\n\n\n=============================================")

    # Import Congressmen
    load_congresspeople_into_db()
    congresspeople = Congressperson.query.all()
    [print(pol) for pol in congresspeople]
    print("\n\n\n=============================================")


    # Import Categories
    load_categories_into_db()
    categories = Category.query.all()
    [print(cat) for cat in categories]
    print("\n\n\n=============================================")

    # Print User Reps
    reps = user.find_representatives()
    [print(rep) for rep in reps]
    print("\n\n\n=============================================")

    # Import Bills
    Bill.retrieve_bills_by_category(Category.query.get(31))
    bills = Bill.query.all()
    [print(bill) for bill in bills]
    print("\n\n\n=============================================")








