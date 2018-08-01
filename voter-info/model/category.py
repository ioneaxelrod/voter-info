from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



########################################################################################################################
# Category definition

class Category(db.Model):
    """"""

    __tablename__ = "categories"

    category_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)

########################################################################################################################
# Helper Functions

def load_categories_into_db():
    with open("subjects.txt") as file:
        categories = []
        for line in file:
            categories.append(Category(name=line))

        db.session.add_all(categories)
        db.session.commit()

########################################################################################################################
# Main Functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///voteinfo'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)




if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app

    connect_to_db(app)
    db.create_all()
    load_categories_into_db()
    print("Connected to DB.")
