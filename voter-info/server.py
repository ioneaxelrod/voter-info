from os import environ

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from jinja2 import StrictUndefined
from sqlalchemy.orm.exc import NoResultFound


from model.congressperson import Congressperson
from model.user import User

app = Flask(__name__)
db = SQLAlchemy()

# Required to use Flask sessions and the debug toolbar
app.secret_key = environ['FLASK_SECRET_KEY']

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


########################################################################################################################
# Home Page


@app.route('/')
def index():
    """Homepage."""

    return render_template("index.html")


########################################################################################################################
# User Pages

@app.route('/profile')
def user_profile():
    """Show user information"""

    user_id = session["user_id"]
    user = User.query.get(user_id)
    return render_template("user_profile.html", user=user)


########################################################################################################################
# Congress Pages

@app.route('/congresspeople')
def show_congress():
    """Creates a page of current congress divided by senators and representatives"""
    representatives = Congressperson.get_representatives()

    senators = Congressperson.get_senators()

    return render_template("congress_list.html", representatives=representatives, senators=senators)


########################################################################################################################
# Registration and Login Pages


@app.route('/register', methods=["GET"])
def register_form():
    """Registration page for new users"""

    return render_template('register_form.html')


@app.route('/register', methods=["POST"])
def register_process():
    """Processes registration. Checks if user exists, if not adds to db """

    username=request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    address = request.form.get("address")

    # Check to see if user exists before registering a new user
    if User.query.filter(or_(User.email == email, User.screen_name == username)).all():
        flash("A user with that email already exists!")

    else:
        # Make a new user
        new_user = User(screen_name=username, email=email, address=address, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("You have successfully registered!")

    return redirect('/')


@app.route('/login')
def login_form():
    """Show page to login as user"""

    return render_template('login_form.html')


@app.route('/login', methods=['POST'])
def login_process():
    """Process login request"""

    # Obtain form information
    username = request.form.get("username")
    password = request.form.get("password")

    # Make sure user actually exists
    try:
        user = User.query.filter(User.screen_name == username).one()
    except NoResultFound:
        flash("Email not registered!")
        return redirect('/')

    # Check to make sure password is correct
    if user.password == password:
        session['user_id'] = user.user_id
        flash("User logged in!")
        return redirect('/profile')
    else:
        flash("Incorrect password!")
        return redirect('/')


@app.route('/logout')
def logout():
    """Log out of user session"""

    del session['user_id']
    flash("Logged out successfully")

    return redirect('/')


########################################################################################################################
# Main Function

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///voteinfo'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')