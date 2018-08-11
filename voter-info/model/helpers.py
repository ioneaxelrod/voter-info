from .db import db
from datetime import datetime
import requests
from .consts import *

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

            from .congressperson import Congressperson

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
    from .category import Category

    with open("subjects.txt") as file:
        categories = []
        for line in file:
            categories.append(Category(name=line))

        db.session.add_all(categories)
        db.session.commit()


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