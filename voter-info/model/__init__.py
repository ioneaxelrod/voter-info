
from .db import db
from .consts import *
from .user import User
from .category import Category
from .congressperson import Congressperson
from .bill import Bill
from .user_category import UserCategory
from .bill_category import BillCategory

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

#
# if __name__ == "__main__":
#     # As a convenience, if we run this module interactively, it will leave
#     # you in a state of being able to work with the database directly.
#
#     from server import app
#
#     connect_to_db(app)
#     db.drop_all()
#     db.create_all()
#
#     print("Connected to DB.")
#     print("\n\n\n=============================================")
#     #
#     #
#     # # Create User
#     # create_dummy_user()
#     # user = User.query.get(1)
#     # print(user)
#     # print("\n\n\n=============================================")
#
#     # Import Congressmen
#     load_congresspeople_into_db()
#     congresspeople = Congressperson.query.all()
#     [print(pol) for pol in congresspeople]
#     print("\n\n\n=============================================")
#
#
#     # Import Categories
#     load_categories_into_db()
#     categories = Category.query.all()
#     [print(cat) for cat in categories]
#     print("\n\n\n=============================================")
#
#     # # Print User Reps
#     # reps = user.find_representatives()
#     # [print(rep) for rep in reps]
#     # print("\n\n\n=============================================")
#
#     # Import Bills
#     for category in categories:
#         try:
#             Bill.parse_bills_by_category(category)
#         except ValueError:
#             print('Decoding JSON has failed')
#
#     print("\n\n\n=============================================")
#
#
#
#




