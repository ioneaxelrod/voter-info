from .db import db
from .helpers import parse_bills_from_json, format_category_name, get_bill_slug
from .consts import *
import requests

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
        from . import BillCategory

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

