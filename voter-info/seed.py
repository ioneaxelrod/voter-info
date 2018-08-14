from model import *
import requests
from model.helpers import parse_name, parse_year
from model.consts import PROPUBLICA_KEY, HOUSE_URL, SENATE_URL
from api_request import parse_bills_by_category, find_representatives
from os import environ

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


def parse_members_from_json(json):
    """Reads a json file and updates database with Congress members
        :param json: ProPublica member json file
        :return None: updates database with information
    """

    members = json["results"][0]['members']

    for member in members:
        if member['in_office'] is False:
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


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app

    connect_to_db(app)
    # db.drop_all()
    db.create_all()

    print("Connected to DB.")
    print("\n\n\n=============================================")
    #
    #
    # # Create User
    # create_dummy_user()
    # user = User.query.get(1)
    # print(user)
    # print("\n\n\n=============================================")

    # Import Congressmen
    load_congresspeople_into_db()
    congresspeople = Congressperson.query.all()

    print("\n\n\n=============================================")

    # # Import Categories
    # load_categories_into_db()
    # categories = Category.query.all()
    # [print(cat) for cat in categories]
    # print("\n\n\n=============================================")

    # # Print User Reps
    # reps = find_representatives(user)
    # [print(rep) for rep in reps]
    print("\n\n\n=============================================")

    # # Import Bills
    # for category in categories:
    #     try:
    #         parse_bills_by_category(category)
    #     except ValueError:
    #         print('Decoding JSON has failed')

    print("\n\n\n=============================================")