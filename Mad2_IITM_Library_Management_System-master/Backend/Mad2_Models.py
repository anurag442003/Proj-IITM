from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
import re




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    uname = db.Column(db.String(50), nullable=False)
    phNumber = db.Column(db.String(15))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    address = db.Column(db.String(255))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    pin = db.Column(db.String(10))
    role = db.Column(db.String(20), nullable=False)
    balance_amt = db.Column(db.Float, default=1000.0)
    ratings = db.relationship('Review', backref='rater', lazy=True)

    def validate_username(self, uname):
        if len(uname) > 20:
            raise ValueError("Username must be at most 20 characters long.")

    def validate_password(self, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search("[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search("[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search("[0-9]", password):
            raise ValueError("Password must contain at least one digit.")
        if not re.search("[!@#$%^&*()-_+=]", password):
            raise ValueError("Password must contain at least one special character.")

    def validate_state(self, state):
        if re.search("[^a-zA-Z\s]", state):
            raise ValueError("State name can only contain alphabets and spaces.")

# class ProfeshionalsDetails(db.Model):
#     pid = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     service_type_id = db.Column(db.Integer, db.ForeignKey('service.id'))
#     experience_years = db.Column(db.Integer)
#     is_verified = db.Column(db.Boolean, default=False)
#     additional_charges=db.Column(db.Float,default=0.00)
    
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(255), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False)
    # profeshional_id = db.Column(db.Integer, db.ForeignKey('profeshionalsdetails.pid'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

# class Service(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), unique=True, nullable=False)

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True) #prof ka id
    title = db.Column(db.String(100), nullable=False) #prof ka name
    author = db.Column(db.String(50), nullable=False) #wont exist anymore, can be desc
    image = db.Column(db.LargeBinary) #prof ka profile photo
    imageType = db.Column(db.String(10)) #idec
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # userid
    ratings = db.relationship('Review', backref='content', lazy=True) #exists
    no_of_pages = db.Column(db.Integer, nullable=False) #experience no of years
    publish_year = db.Column(db.Integer, nullable=False) #birthday
    file = db.Column(db.LargeBinary, nullable=False) #resume
    pdf_file_name = db.Column(db.String(250), nullable=True) #not needed
    #is_verified = db.Column(db.Boolean, default=False)
    price = db.Column(db.Float, nullable=False) #additional charge
    section = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False) #servicetype
    borrowings = db.relationship('Borrowing', backref='borrowed_content',  cascade="all, delete-orphan") #service request backref to request
    # wishlists = db.relationship('Wishlist', backref='wishlisted_content',  cascade="all, delete-orphan") #not needed

class TransactionsLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    content_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.now, nullable=False)

class Borrowing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    returned = db.Column(db.Boolean, default=False)
    return_date = db.Column(db.DateTime)
    last_return_date = db.Column(db.DateTime)
    reissue_count = db.Column(db.Integer, default=0)
    is_read = db.Column(db.Boolean, default=False)


class Requests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contentId = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    response = db.Column(db.String(10), default='Pending')

# class Wishlist(db.Model): #not needed
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False)
#     user = db.relationship('User', backref='wishlist_items', lazy=True)
#     content = db.relationship('Content', back_populates='wishlists', lazy=True, overlaps="wishlisted_content")

class Login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    last_login_time = db.Column(db.DateTime, default=datetime.now, nullable=False)

class Purchase(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False)