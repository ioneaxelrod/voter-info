from datetime import datetime


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


# Helper Functions

def format_category_name(category):
    """Cleans up category name so it can be placed into GET request
        :param category: Category
        :return str: reformatted string without certain characters
    """

    category_words = category.name.rstrip().replace(',', '').replace("'", '').split(" ")
    return "-".join(category_words)


def get_bill_slug(bill_id):
    """Formats bill_id into bill slug
        :param bill_id: bill_id of bill we want slug for
        :return str: bill slug
    """

    return bill_id.split("-")[0]
