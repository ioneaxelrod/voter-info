from .db import db
from .category import Category
from .bill import Bill


class BillCategory(db.Model):
    """BillCategory for Voter Info Project"""

    __tablename__ = "bill_categories"

    bill_category_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    category_id = db.Column(db.Integer)

    category_id = db.Column(db.Integer, db.ForeignKey(Category.category_id))
    bill_id = db.Column(db.String, db.ForeignKey(Bill.bill_id))

    category = db.relationship("Category", backref="bill_categories")
    bill = db.relationship("Bill", backref="bill_categories")