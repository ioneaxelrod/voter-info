from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime
import requests


HOUSE_URL = "https://api.propublica.org/congress/v1/115/house/members.json"
SENATE_URL = "https://api.propublica.org/congress/v1/115/senate/members.json"
BILL_BY_CATEGORY_URL= "https://api.propublica.org/congress/v1/bills/subjects/{subject}.json"
REPRESENTATIVE_URL = "https://www.googleapis.com/civicinfo/v2/representatives?key="
ROLL_CALL_URL = "https://api.propublica.org/congress/v1/115/bills/{bill-id}.json"
VOTE_URL = "https://api.propublica.org/congress/v1/115/{chamber}/sessions/{session-number}/votes/{roll-call-number}.json"

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
        """Finds the politicians that represent the user based on user's address
        :return [Congressperson]: congresspeople associated with User's address
        """

        # Retrieves json from google api to get json of local politicians
        search_address = "&address=" + self.address
        request = requests.get(REPRESENTATIVE_URL + CIVIC_KEY + search_address)
        politician_json = request.json()

        politician_info = politician_json['officials']

        # instantiate list for politicians and loop through json
        congresspeople = []
        for politician in politician_info:
            # eliminate middle names so we can find politicians based on first and last name
            name = remove_middle_name(politician['name'])

            # check if congressperson is in database, if so, add them to list
            congressperson = Congressperson.query.filter_by(name=name).first()

            if congressperson:
                congresspeople.append(congressperson)
        return congresspeople

    def add_user_categories(self, categories):
        """Adds a list of categories associated with user to database
            :param categories: categories to be added that will now be associated with User instance
            :type categories: list of Category
            :return None: UserCategories are added to database
        """

        added_categories = []

        for category in categories:
            # Only append user_categories if they are not in database, we do not want multiple copies of same category
            if not UserCategory.query.filter(UserCategory.user_id == self.user_id,
                                             UserCategory.category_id == category.category_id).first():
                added_categories.append(UserCategory(user_id=self.user_id, category_id=category.category_id))

        db.session.add_all(added_categories)
        db.session.commit()


# Helper Functions

def remove_middle_name(name):
    """Removes middle name from politician for easier integration of conflicting apis
        :param name: string representing name of politician
        :return str: name without middle name
    """

    name_parts = name.split(" ")
    for part in name_parts:
        if '.' in part:
            name_parts.remove(part)
    return " ".join(name_parts)


########################################################################################################################
# Category definition

class Category(db.Model):
    """Category for Voter Info Project"""

    __tablename__ = "categories"

    category_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)

########################################################################################################################
# Congressperson definition

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





# Helper Functions

def parse_vote_from_json(json, congressperson):
    """Parses json to get congressperson's vote data
    :param json: vote JSON file from ProPublica
    :param congressperson: Congressperson
    :return str: vote position associated with congressperson"""

    if json.get('error') or json.get('errors') or json.get('status') == "ERROR":
        print("No results found")
        return

    vote_positions = json['results']['votes']['vote']['positions']
    print()
    print()
    print()
    print("======================================")

    for position in vote_positions:
        if position['member_id'] == congressperson.congress_id:
            vote = position['vote_position']
            print(vote)
            return vote

    return "No vote information found"

def parse_members_from_json(json):
    """Reads a json file and updates database with Congress members
        :param json: ProPublica member json file
        :return None: updates database with information
    """

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
    """Creates a singular name string by combining first and last name
        :param first_name: str representing first name of congressperson
        :param last_name: str representing last name of congressperson
        :return str: full name of congressperson
    """

    return first_name + " " + last_name


def parse_year(year):
    """Shows year given a datetime
        :param year: str
        :return Datetime
    """

    return datetime.strptime(year, '%Y')


########################################################################################################################
# Bill definition

class Bill(db.Model):
    """Bill for Voter Info Project"""

    __tablename__ = "bills"

    bill_id = db.Column(db.String,
                        unique=True,
                        nullable=False,
                        primary_key=True)
    bill_title = db.Column(db.String)
    bill_uri = db.Column(db.String, unique=True, nullable=False)
    summary = db.Column(db.String)
    house_roll_call = None
    senate_roll_call = None
    house_votes_url = None
    senate_votes_url = None

    @classmethod
    def parse_bills_by_category(cls, category):
        """Grabs 20 most recent bills from ProPublica api associated with specific subject/category
            :param category: Category which you want to associate bills with
            :return None: Update database with bills associated with category
        """

        # Create subject so it can be passed into REST call and place in URL
        subject = format_category_name(category)
        search_url = BILL_BY_CATEGORY_URL.replace("{subject}", subject)
        print(search_url)

        # Send request and parse it
        fill_bill_request = requests.get(search_url, headers={'X-API-Key': PROPUBLICA_KEY})
        print(fill_bill_request.text)
        bill_json = fill_bill_request.json()

        parse_bills_from_json(bill_json, category)

    @classmethod
    def retrieve_bills_by_category(cls, category):
        """Gets bills associated with category from database
            :param category: Category you want bills to be associated with
            :return [Bill]: bills of the category you want
        """

        return Bill.query.join(BillCategory).filter_by(category_id=category.category_id).all()

    def set_roll_call_info(self):
        """Sets roll call data so we can look up how politicians voted
            :return None: sets bill's roll call info
        """

        # Create bill slug, then use it to call ProPublica api
        bill_slug = get_bill_slug(self.bill_id)
        search_url = ROLL_CALL_URL.replace("{bill-id}", bill_slug)
        print(search_url)

        fill_bill_request = requests.get(search_url, headers={'X-API-Key': PROPUBLICA_KEY})
        print(fill_bill_request.text)

        bill_json = fill_bill_request.json()

        # Check to make sure there is no error in information received, then parse the info
        if bill_json.get('error') or bill_json.get('errors') or bill_json.get('status') == "ERROR":
            print("No results found")

        else:
            results = bill_json['results'][0]['votes']
            if results:
                self.parse_roll_call_info(results)


    def parse_roll_call_info(self, json_results):
        """Takes a bill json and checks for roll call info.
            :param json_results: dictionary of results cleaned up
            :return None: if there are any votes, they are added to bill's information.
        """

        # Iterate through once to get first house result which is the most recent vote
        for result in json_results:
            if result['chamber'] == 'House':
                self.house_roll_call = result['roll_call']
                self.house_votes_url = result['api_url']
                break

        # Iterate through once to get first senate result which is the most recent vote
        for result in json_results:
            if result['chamber'] == 'Senate':
                self.senate_roll_call = result['roll_call']
                self.senate_votes_url = result['api_url']
                break


# Helper Functions

def format_category_name(category):
    """Cleans up category name so it can be placed into GET request
        :param category: Category
        :return str: reformatted string without certain characters
    """

    category_words = category.name.rstrip().replace(',', '').replace("'", '').split(" ")
    return "-".join(category_words)


def parse_bills_from_json(json, category):
    """Takes bill json and category and updates database with new bill information
        :param json: Bill JSON
        :param category: Category
        :return None: updates database with new bill information
    """

    # Check to make sure there are no errors in database
    if json.get('error') or json.get('errors') or json.get('status') == "ERROR":
        print("No results found")
        return

    bills = json['results']
    for bill in bills:

        bill_id = bill['bill_id']

        # Check to see if bill already exists, if so just add new BillCategory
        if Bill.query.filter_by(bill_id=bill_id).first():
            bill_category = BillCategory(bill_id=bill_id, category_id=category.category_id)
            db.session.add(bill_category)

        # Parse JSON and get information needed
        else:
            bill_title = bill['short_title']
            bill_uri = bill['congressdotgov_url']
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

def get_bill_slug(bill_id):
    """Formats bill_id into bill slug
        :param bill_id: bill_id of bill we want slug for
        :return str: bill slug
    """

    return bill_id.split("-")[0]


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
    """BillCategory for Voter Info Project"""

    __tablename__ = "bill_categories"

    bill_category_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    category_id = db.Column(db.Integer)

    category_id = db.Column(db.Integer, db.ForeignKey(Category.category_id))
    bill_id = db.Column(db.String, db.ForeignKey(Bill.bill_id))

    category = db.relationship("Category", backref="bill_categories")
    bill = db.relationship("Bill", backref="bill_categories")


########################################################################################################################
# Vote definition
#
# class Vote(db.Model):
#     """"""
#
#     __tablename__ = "votes"
#
#     vote_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     vote_position = db.Column(db.String, nullable=False)
#     congress_id = db.Column(db.String, db.ForeignKey(Congressperson.congress_id))
#     bill_id = db.Column(db.String, db.ForeignKey(Bill.bill_id))
#
#     category = db.relationship("Category", backref="bill_categories")
#     bill = db.relationship("Bill", backref="bill_categories")

########################################################################################################################
# Seeding Data Functions

def create_dummy_user():
    """Creates a default user for testing out web app
        :return None
    """

    user = User(screen_name="ione",
                email="ione@ione.com",
                password=environ["IONE_PASS"],
                address="Stoneridge Dr, Pleasanton, CA, 94588")
    db.session.add(user)
    db.session.commit()


def load_congresspeople_into_db():
    """Loads all members of Congress into database
    :return None
    """

    # load senators
    fill_senate_request = requests.get(SENATE_URL, headers={'X-API-Key': PROPUBLICA_KEY})
    senate_json = fill_senate_request.json()
    parse_members_from_json(senate_json)

    # load representatives
    fill_house_request = requests.get(HOUSE_URL, headers={'X-API-Key': PROPUBLICA_KEY})
    house_json = fill_house_request.json()
    parse_members_from_json(house_json)


def load_categories_into_db():
    """Loads categories into database from text file
        :return None
    """
    with open("subjects.txt") as file:
        categories = []
        for line in file:
            categories.append(Category(name=line))

        db.session.add_all(categories)
        db.session.commit()


########################################################################################################################
# Main Functions

def connect_to_db(app):
    """Connect the database to our Flask app.
    :param app: Flask application
    :return None
    """

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
    for category in categories:
        try:
            Bill.parse_bills_by_category(category)
        except ValueError:
            print('Decoding JSON has failed')

    print("\n\n\n=============================================")








