from .db import db


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

