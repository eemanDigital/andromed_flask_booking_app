from andromeda import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates
from validate_email import validate_email  # Package: py3-validate-email


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    phone_number = db.Column(db.String(30))

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # An example of validation
    @validates('email')
    def validate_email(self, key, address):
        try:
            # check: https://pypi.org/project/py3-validate-email/
            validate_email(email_address=address,
                           use_blacklist=True,
                           # If true checks the mx-records and
                           # check whether the email actually exists
                           check_mx=False,
                           check_regex=True)
        except AssertionError as error:
            print(error)

    def __init__(self, username, email, password, phone_number=None):
        self.username = username
        self.email = email
        self.password = password
        self.phone_number = phone_number

    def __repr__(self):
        return (f"User('{self.username}','{self.email}')")


class Company(db.Model):
    __tablename__ = "company"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone_number = db.Column(db.String(30))
    ticket_quota = db.Column(db.Integer)

    def __init__(self, name, email, phone_number=None, ticket_quota=0):
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.ticket_quota = ticket_quota

    def __repr__(self):
        return f"Company('{self.name}', '{self.email}')"


class Country(db.Model):
    __tablename__ = "country"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    cities = db.relationship('City',
                             back_populates="country",
                             lazy=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return (f"Country('{self.name}')")


class City(db.Model):
    __tablename__ = "city"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)  # Not unique
    country_id = db.Column(db.Integer,
                           db.ForeignKey('country.id'),
                           nullable=False)
    country = db.relationship('Country',
                              back_populates="cities",
                              lazy=True)

    def __init__(self, name, country_id):
        self.name = name
        self.country_id = country_id

    def __repr__(self):
        return (f"City('{self.name}', '{self.country_id}')")
