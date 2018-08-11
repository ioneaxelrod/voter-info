from .db import db
from .user import User
from .category import Category


class UserCategory(db.Model):
    """"""

    __tablename__ = "user_categories"

    user_category_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey(Category.category_id), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.user_id), nullable=False)

    category = db.relationship("Category", backref="user_categories")
    user = db.relationship("User", backref="user_categories")
