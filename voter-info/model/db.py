from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_to_db(app):
    """Connect the database to our Flask app.
    :param app: Flask application
    :return None
    """

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///voteinfo'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
