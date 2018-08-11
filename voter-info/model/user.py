from .db import db
import requests
from .consts import *
from .helpers import remove_middle_name

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
        from . import Congressperson

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
        from . import UserCategory

        added_categories = []

        for category in categories:
            # Only append user_categories if they are not in database, we do not want multiple copies of same category
            if not UserCategory.query.filter(UserCategory.user_id == self.user_id,
                                             UserCategory.category_id == category.category_id).first():
                added_categories.append(UserCategory(user_id=self.user_id, category_id=category.category_id))

        db.session.add_all(added_categories)
        db.session.commit()

    # def remove_user_categories(self, categories):
    #     """
    #
    #         :param categories:
    #         :return:
    #     """
    #
    #     for category in categories:
    #         if UserCategory.query.filter(UserCategory.user_id == self.user_id,
    #                                      UserCategory.category_id == category.category_id).first():
    #             db.session.

