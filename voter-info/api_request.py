from model import db, Congressperson, BillCategory, Bill
from model.helpers import remove_middle_name
from model.consts import REPRESENTATIVE_URL, CIVIC_KEY, BILL_BY_CATEGORY_URL, PROPUBLICA_KEY
from model.helpers import format_category_name
import requests


def find_representatives(user):
    """Finds the politicians that represent the user based on user's address
    :param user: user whose representatives you want to find
    :return [Congressperson]: congresspeople associated with User's address
    """

    # Retrieves json from google api to get json of local politicians
    search_address = "&address=" + user.address
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


def parse_bills_by_category(category):
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
