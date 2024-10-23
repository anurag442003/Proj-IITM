from flask import Flask, Blueprint, send_file, abort, jsonify, request , redirect, url_for , make_response
from flask_restful import Api, Resource , reqparse 
import json
from werkzeug.exceptions import HTTPException
import os
from flask_mail import Mail, Message
from flask_cors import CORS
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import aliased
from sqlalchemy import or_, distinct
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from datetime import datetime, timedelta, timezone
from PIL import Image
from io import BytesIO
from html import escape
from PyPDF2 import PdfReader
from flask_caching import Cache
import matplotlib.pyplot as plt
import logging
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    get_jwt_identity,
    create_access_token,
    get_jwt,
    set_access_cookies,
    unset_jwt_cookies,
    decode_token
)
from werkzeug.utils import secure_filename
import imghdr
from functools import wraps
import base64
import numpy as np
from celery import Celery, Task
from celery.schedules import crontab
from reportlab.pdfgen import canvas
import flask_excel as excel
from celery.result import AsyncResult

class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///Mad2_TheWisdom.db'
    JWT_SECRET_KEY = '23f1001674'
    JWT_ACCESS_TOKEN_EXPIRES = 7200
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    broker = 'redis://localhost:6379/0'
    result_backend = 'redis://localhost:6379/0'
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    CACHE_TYPE = 'RedisCache'
    # CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL') or 'redis://localhost:6379'
    CACHE_REDIS_HOST = 'localhost'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB=3
    CACHE_DEFUALT_TIMEOUT=300

app = Flask(__name__)
app.config.from_object(Config)


logging.basicConfig(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logging.getLogger().addHandler(stream_handler)


from Mad2_Models import db, User, Section, Content, Borrowing, TransactionsLog, Review, Wishlist, Login, Purchase, Requests
db.init_app(app)
api = Api(app)
excel.init_excel(app)
migrate = Migrate(app, db)
mail = Mail(app)
bcrypt = Bcrypt(app)
cache = Cache(app)
jwt = JWTManager(app)
blacklisted_tokens = set()
CORS(app)


def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery
celery = make_celery(app)

celery.conf.beat_schedule = {
    'send_email-inactive': {
        'task': 'send_email',
        'schedule': crontab(minute="*/10"),
    },
    'monthly_report': {
        'task': 'monthly_report',
        'schedule': crontab(minute="*/10")
    },
    'revoke_access': {
        'task': 'revoke_access',
        'schedule': crontab(minute="*/10")
    },
    'delete_rej_issue': {
        'task': 'delete_rejected_issue_requests',
        'schedule': crontab(minute="*/10")
    }
}

@celery.task(name="send_email")
def desert_user():
    threshold_time = datetime.now() - timedelta(days=1)
    inactive_users = User.query.join(Login).filter(Login.last_login_time < threshold_time).all()
    for user in inactive_users:
        subject = 'Reminder: Log in to our Library Management System'
        body = f'Dear {user.fname},\n\nThis is a reminder to log in to our Library Management System.'
        sender = "noreply@app.com"
        msg = Message(subject, sender=sender, recipients=[user.email], body=body)
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Failed Sending Email: {e}")

@celery.task(name="monthly_report")
def monthly_report():
    try:
        all_users = User.query.all()
        for user in all_users:
            active_borrowings_count = Borrowing.query.filter_by(member_id=user.id, returned=False).count()
            wishlist_items_count = len(user.wishlist_items)

            pdf_buffer = BytesIO()
            c = canvas.Canvas(pdf_buffer)
            c.drawString(100, 750, "Monthly Report for User: {}".format(user.uname))
            c.drawString(100, 730, "Active Borrowings: {}".format(active_borrowings_count))
            c.drawString(100, 710, "Wishlist Items Count: {}".format(wishlist_items_count))
            c.save()

            sender = "noreply@app.com"
            msg = Message("Monthly Report", sender=sender, recipients=[user.email])
            msg.body = "Please find attached the monthly report."
            msg.attach("monthly_report.pdf", "application/pdf", pdf_buffer.getvalue())
            mail.send(msg)
    except Exception as e:
        print(f"Failed to generate monthly reports: {e}")

@celery.task(name="revoke_access")
def revoke_access():
    expired_borrowings = Borrowing.query.filter(Borrowing.last_return_date < datetime.now()).all()
    for borrowing in expired_borrowings:
        borrowing.returned = True
        borrowing.return_date = datetime.now()
        borrowing.is_read = True
    db.session.commit()

@celery.task(name="delete_rejected_issue_requests")
def delete_rejected_issue_requests():
    try:
        rejected_issue_requests = Requests.query.filter_by(response="Rejected").all()
        for issue_request in rejected_issue_requests:
            db.session.delete(issue_request)
        db.session.commit()
    except Exception as e:
        print(f"Failed to delete rejected issue requests: {e}")

@celery.task(name="create_csv")
def create_csv():
    try:
        tl = TransactionsLog.query.all()
        csv_file_path = 'transaction_logs.csv'
        

        csv_output = excel.make_response_from_query_sets(
            tl, 
            ['id', 'user_id', 'action', 'content_id', 'timestamp'], 
            'csv'
        )
        

        with open(csv_file_path, 'wb') as f:
            f.write(csv_output.get_data())
        
        return {'csv_file_path': csv_file_path}
    except Exception as e:
        print(f"Failed to download csv issue requests: {e}")
        return {'error': str(e)}


@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        app.logger.info(f"Received login data: {data}")

        user = User.query.filter(
            or_(User.email == data["input"], User.uname == data["input"])
        ).first()

        if user:
            app.logger.info(f"User found: {user.uname}")
            if bcrypt.check_password_hash(user.password, data["password"]):
                login = Login.query.filter_by(user_id=user.id).first()

                if login:
                    login.last_login_time = datetime.now()
                else:
                    login = Login(
                        user_id=user.id, last_login_time=datetime.now()
                    )
                    db.session.add(login)

                db.session.commit()

                additional_claims = {
                    "id": user.id,
                    "role": user.role,
                    "username": user.uname,
                    "email": user.email,
                }
                access_token = create_access_token(
                    identity=user.id, additional_claims=additional_claims
                )

                app.logger.info("Login Successfully!")
                return jsonify({"message": "Login successful!", "token": access_token}), 200
            else:
                app.logger.warning("Incorrect password")
                return jsonify({"error": "Invalid password"}), 401
        else:
            app.logger.warning("User not found")
            return jsonify({"error": "Invalid email/username"}), 401
    except Exception as e:
        app.logger.error(f"Error Logging In: {str(e)}")
        return jsonify({"error": "Login Failed", "reasons": str(e)}), 500



def token_not_in_blacklist(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        jti = get_jwt()["jti"]
        if jti in blacklisted_tokens:
            return jsonify({"error": "Token has been revoked"}), 401
        return fn(*args, **kwargs)

    return wrapper

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_data):
    jti = jwt_data['jti']
    return jti in blacklisted_tokens


@app.route("/logout", methods=["POST"])
@jwt_required()
@token_not_in_blacklist
def logout():
    try:
        jti = get_jwt()["jti"]

        blacklisted_tokens.add(jti)
        unset_jwt_cookies()

        return jsonify({"message": "Logout successfully!"}), 200
    except Exception as e:
        return jsonify({"error": "Logout failed", "Reasons": str(e)}), 500



@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()

        hashed_password = bcrypt.generate_password_hash(data["password"]).decode(
            "utf-8"
        )

        new_user = User(
            fname=data["firstname"],
            lname=data["lastname"],
            uname=data["username"],
            phNumber=data["phoneNumber"],
            email=data["email"],
            password=hashed_password,
            gender=data["gender"],
            address=data["address"],
            city=data["city"],
            state=data["state"],
            pin=data["zip"],
            role=data["role"],
        )

        db.session.add(new_user)
        db.session.commit()
        print("1 user register")
        app.logger.info('User Registered Successfully!')
        return jsonify({"message": "Registration successful!!"}), 201
    except Exception as e:
        print("2 User not register")
        app.logger.error('User Registered Failed')
        return jsonify({"error": "Registration Failed", "Reasons": str(e)}), 500


@app.route("/verify", methods=["OPTIONS"])
def handle_options():
    response = jsonify({"message": "CORS preflight request successful!"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    return response



@app.route("/verify", methods=["GET"])
def verify_token():
    try:
        token = request.headers.get("Authorization")
        user = validate_token_and_get_user(token)

        if user:
            app.logger.info("User Present")
            return (
                jsonify(
                    {
                        "authenticated": True,
                        "user": {"id": user.id, "username": user.uname, "role": user.role},
                    }
                ),
                200,
            )
        else:
            app.logger.warning("No User Found")
            return jsonify({"authenticated": False}), 401

    except Exception as e:
        app.logger.info("Error: Verifying Token")
        return jsonify({"error": "Error verifying Token", "Reasons": str(e)}), 500


def validate_token_and_get_user(token):
    try:
        if token:

            @jwt_required()
            def get_user_from_token():
                user_id = get_jwt_identity()
                user = User.query.filter_by(id=user_id).first()
                return user

            return get_user_from_token()
        else:
            return None
    except Exception as e:
        print("Exception during token validation:", str(e))
        return None

@app.route('/download-csv', methods=['GET'])
def download_csv():
    task = create_csv.delay()
    return jsonify({'task_id': task.id})

@app.route('/get-csv/<task_id>', methods=['GET'])
def get_csv(task_id):
    res = celery.AsyncResult(task_id)
    if res.ready():
        result = res.result
        if 'csv_file_path' in result:
            return send_file(result['csv_file_path'], as_attachment=True)
        else:
            return jsonify({"message": "Error generating CSV", "error": result.get('error')}), 500
    else:
        return jsonify({"message": "Task Pending"}), 202





#ADD
# 1. Section
@app.route("/section", methods=["POST"])
@jwt_required()
def create_section():
    try:
        data = request.get_json()

        existing_Section = Section.query.filter_by(name=data["name"]).first()
        if existing_Section:
            return jsonify({"error": "Section already exists , Please add new Section"}), 400

        new_section = Section(name=data["name"])
        db.session.add(new_section)
        db.session.commit()

        return jsonify({"message": "Section created successfully!!"}), 201
    except Exception as e:
        return jsonify({"error": "New Section creation is failed", "Reasons": str(e)}), 500

# 2. Content
@app.route("/add-content/<int:section_id>/<int:user_id>", methods=["POST"])
@jwt_required()
def add_content(section_id, user_id):

    current_user_id = get_jwt_identity()

    if current_user_id != user_id:
        app.logger.error("User is unauthorized")
        return jsonify({"message": "Unauthorized"}), 401

    section = Section.query.get(section_id)
    if not section:
        app.logger.error("Section Not Found")
        return jsonify({"message": "Invalid section_id"}), 400
    

    if 'image' not in request.files:
        app.logger.error("Image is not found")
        return jsonify({"message": "Image is required"}), 400

    if 'pdf' not in request.files:
        app.logger.error("PDF file is missing")
        return jsonify({"message": "PDF file is required"}), 400

    try:
        title = escape(request.form.get("title"))
        author = escape(request.form.get("author"))
        no_of_pages = escape(request.form.get("number_of_pages"))
        price = escape(request.form.get("price"))
        publish_year = escape(request.form.get("publish_year"))

        if not all([title, author, no_of_pages, publish_year, price, ]):
            app.logger.warn("Data Is Incomplete")
            return jsonify({"message": "Incomplete form data"}), 400

        content = Content(
            title=title,
            author=author,
            no_of_pages=no_of_pages,
            publish_year=publish_year,
            price=price,
            section=section_id,
            uploaded_by_id=user_id,
        )

        if "image" in request.files:
            image = request.files["image"]
            if image:
                filename = secure_filename(image.filename)
                image_data = image.read()
                image_type = imghdr.what(None, h=image_data)
                content.image = image_data
                content.imageType = image_type

        if "pdf" in request.files:
            pdf = request.files["pdf"]
            if pdf:
                filename = secure_filename(pdf.filename)
                pdf_data = pdf.read()

                try:
                    pdf_reader = PdfReader(pdf)
                    if len(pdf_reader.pages) == 0:
                        app.logger.warning("No Pages Available In PDF")
                        return (
                            jsonify({"message": "Invalid PDF file: No pages found"}),
                            400,
                        )
                    else:
                        content.no_of_pages = len(pdf_reader.pages)
                except Exception as e:
                    app.logger.error("Invalid PDF File")
                    return jsonify({"message": f"Invalid PDF file: {str(e)}"}), 400

                content.pdf_file_name = filename
                content.file = pdf_data
        else:
            content.file = None

        db.session.add(content)
        db.session.commit()

        app.logger.info("Content Added Successfully")
        return jsonify({"message": "Content added successfully"}), 201

    except Exception as e:
        app.logger.error("Error Adding Content", str(e))
        return jsonify({"message": f"Error adding content: {str(e)}"}), 500

# 3. Wishlist
@app.route("/wishlist/add/<int:content_id>", methods=["POST"])
@jwt_required()
def add_to_wishlist(content_id):
    try:
        current_user_id = get_jwt_identity()

        existing_wishlist_item = Wishlist.query.filter_by(
            content_id=content_id, user_id=current_user_id
        ).first()

        if existing_wishlist_item:
            app.logger.warn("Content Already In Wishlist")
            return jsonify({"error": "Content is already in the wishlist"}), 400

        new_wishlist_item = Wishlist(content_id=content_id, user_id=current_user_id)
        db.session.add(new_wishlist_item)

        new_transaction_log = TransactionsLog(
            user_id=current_user_id,
            action="+ Wishlist",
            content_id=content_id,
            timestamp=datetime.now(),
        )
        db.session.add(new_transaction_log)

        db.session.commit()

        app.logger.info("Content Wishlisted Successfully")
        return jsonify({"message": "Content added to wishlist successfully"}), 200
    except Exception as e:
        app.logger.error("Content Wishlisting Failed", str(e))
        return (
            jsonify({"error": "Failed to add content to wishlist", "details": str(e)}),
            500,
        )



#Fetch
# 1. Sections
@app.route("/fetch-sections", methods=["GET"])
def get_all_sections():
    try:
        sections = Section.query.all()


        sections_list = [
            {"id": section.id, "name": section.name} for section in sections
        ]

        app.logger.info("Fetched Sections")
        return jsonify({"sections": sections_list})
    except Exception as e:
        app.logger.error("Fetching Sections Failed")
        return jsonify({"error": "Failed to fetch sections", "Reasons": str(e)}), 500

# 2. Content
@app.route("/fetch-content", methods=["GET"])
def fetch_content():
    try:
        contents = Content.query.all()

        formatted_contents = []
        for content in contents:
            ratings = Review.query.filter_by(content_id=content.id).all()
            average_rating = round(sum(rating.rating for rating in ratings) / len(ratings), 2) if ratings else 0

            formatted_content = {
                "id": content.id,
                "title": content.title,
                "author": content.author,
                "rating": average_rating,
                "section": content.section,
                "imageType": content.imageType,
                "image": base64.b64encode(content.image).decode("utf-8"),
                "ratings": [
                    {
                        "id": rating.id,
                        "rating": rating.rating,
                        "comment": rating.comment,
                        "user_id": rating.user_id
                    }
                    for rating in ratings
                ]
            }
            formatted_contents.append(formatted_content)

        app.logger.info("Content Fetched Successfully")
        return jsonify({"contents": formatted_contents})

    except Exception as e:
        app.logger.error("Error Fetching Content", str(e))
        return jsonify({"error": "Failed to fetch content", "details": str(e)}), 500

# 3. InDemand
@app.route('/fetch-InDemand', methods=['GET'])
def fetch_InDemand_contents():
    try:
        InDemand_contents = db.session.query(Content, func.avg(Review.rating).label('avg_rating')) \
            .join(Review) \
            .group_by(Content.id) \
            .order_by(func.avg(Review.rating).desc()) \
            .limit(15) \
            .all()
        serialized_contents = []
        for content, avg_rating in InDemand_contents:
            serialized_content = {
                'id': content.id,
                'title': content.title,
                'author': content.author,
                'rating': round(avg_rating or 0, 2),
                'image': content.image,
                'imageType': content.imageType,
                "image": base64.b64encode(content.image).decode("utf-8"),
                'average_rating': avg_rating
            }
            serialized_contents.append(serialized_content)
        
        app.logger.info("Fetched InDemand Content Successfully")
        return jsonify({'contents': serialized_contents}), 200
    except Exception as e:
        app.logger.error("Error Fetching InDemand Content", str(e))
        return jsonify({'error': str(e)}), 500

# 4. User Content
@app.route("/user/fetch-content/<int:user_id>", methods=["GET"])
def fetch_user_content(user_id):
    try:
        contents = (
            Content.query.outerjoin(
                Borrowing,
                (Borrowing.content_id == Content.id) & (Borrowing.member_id == user_id),
            )
            .outerjoin(
                Wishlist,
                (Wishlist.content_id == Content.id) & (Wishlist.user_id == user_id),
            )
            .outerjoin(Review, Review.content_id == Content.id)
            .outerjoin(
                Requests,
                (Requests.contentId == Content.id) & (Requests.userId == user_id),
            )
            .add_columns(
                Content.id,
                Content.title,
                Content.author,
                Content.section,
                func.avg(Review.rating).label("rating"),
                Content.imageType,
                Content.image,
                Borrowing.returned.label("returned"),
                Borrowing.id.label("borrowing_id"),
                Wishlist.id.label("wishlist_id"),
                Requests.response.label("isRequested"),
            )
            .group_by(Content.id)
            .all()
        )

        formatted_contents = [
            {
                "id": content.id,
                "title": content.title,
                "author": content.author,
                "section": content.section,
                "rating": round(content.rating or 0, 2),
                "imageType": content.imageType,
                "image": base64.b64encode(content.image).decode("utf-8"),
                "isIssued": content.borrowing_id is not None and not content.returned,
                "isWishlisted": content.wishlist_id is not None,
                "isRead": content.borrowing_id is not None,
                "isRequested": content.isRequested == 'Pending' if content.isRequested else False
            }
            for content in contents
        ]
        app.logger.info("Content Fetched by User-ID Successful")

        return jsonify({"contents": formatted_contents})

    except Exception as e:
        app.logger.error("Content Fetched by User-ID Failed: %s", str(e))
        return ( 
            jsonify({"error": "Failed to fetch user content", "details": str(e)}),
            500,
        )

# 5. Conent Details
@app.route("/fetch-content-details/<int:content_id>", methods=["GET"])
@jwt_required()
def fetch_content_details(content_id):
    content = Content.query.get(content_id)

    if content:
        content_details = {
            "image": base64.b64encode(content.image).decode("utf-8"),
            "title": content.title,
            "author": content.author,
            "price": content.price,
            "publish_year": content.publish_year,
        }

        app.logger.info("Content Fetched by Content-ID Successfully")
        return jsonify(content_details)
    else:
        app.logger.error("Content Fetched by Content-ID Failed")
        return jsonify({"message": "Content not found"}), 404


#DELETE
# 1. Section
@app.route("/remove-section/<int:section_id>", methods=["DELETE"])
@jwt_required()
def delete_section(section_id):
    try:
        section = Section.query.get(section_id)

        if section:
            Content.query.filter_by(section=section_id).delete()

            db.session.delete(section)
            db.session.commit()
            app.logger.info("Section Deleted Successfully!")
            return jsonify({"message": "Section and associated contents deleted successfully!"}), 200
        else:
            app.logger.warning("Failed Deleting Section")
            return jsonify({"error": "Section not found"}), 404
    except IntegrityError:
        db.session.rollback()
        app.logger.error("Error Deleting Section: IntegrityError")
        return jsonify({"error": "Section deletion failed due to integrity error"}), 500
    except Exception as e:
        app.logger.error("Error Deleting Section", str(e))
        return jsonify({"error": "Section deletion failed", "Reasons": str(e)}), 500

# 2. Content
@app.route("/delete-content/<int:content_id>", methods=["DELETE"])
@jwt_required()
def delete_content(content_id):
    try:
        content = Content.query.get(content_id)
        if not content:
            app.logger.warning("Content not found: %s", content_id)
            return jsonify({"error": "Content not found"}), 404

        app.logger.info("Content found: %s", content_id)

        try:
            related_wishlist_items = Wishlist.query.filter_by(content_id=content_id).all()
            app.logger.info("Found %d related wishlist items", len(related_wishlist_items))
            for wishlist_item in related_wishlist_items:
                db.session.delete(wishlist_item)
        except Exception as e:
            app.logger.error("Error deleting wishlist items: %s", str(e))
            return jsonify({"error": "Failed to delete wishlist items", "details": str(e)}), 500

        try:
            related_review_items = Review.query.filter_by(content_id=content_id).all()
            app.logger.info("Found %d related review items", len(related_review_items))
            for review_item in related_review_items:
                db.session.delete(review_item)
        except Exception as e:
            app.logger.error("Error deleting review items: %s", str(e))
            return jsonify({"error": "Failed to delete review items", "details": str(e)}), 500
        try:
            related_borrowing_items = Borrowing.query.filter_by(content_id=content_id).all()
            app.logger.info("Found %d related borrowing items", len(related_borrowing_items))
            for borrow_item in related_borrowing_items:
                db.session.delete(borrow_item)
        except Exception as e:
            app.logger.error("Error deleting borrowing items: %s", str(e))
            return jsonify({"error": "Failed to delete borrowing items", "details": str(e)}), 500

        try:
            db.session.delete(content)
            db.session.commit()
        except Exception as e:
            app.logger.error("Error deleting content: %s", str(e))
            return jsonify({"error": "Failed to delete content", "details": str(e)}), 500

        app.logger.info("Content and related items deleted successfully")
        return jsonify({"message": "Content and related items deleted successfully"}), 200

    except Exception as e:
        app.logger.error("Unexpected error: %s", str(e))
        return jsonify({"error": "Content deletion failed", "details": str(e)}), 500

# 3. Wishlist
@app.route("/wishlist/remove/<int:content_id>", methods=["POST"])
@jwt_required()
def remove_from_wishlist(content_id):
    try:
        current_user_id = get_jwt_identity()

        wishlist_item = Wishlist.query.filter_by(
            content_id=content_id, user_id=current_user_id
        ).first()

        if not wishlist_item:
            app.logger.warn("Content Not Found In Wishlisted")
            return jsonify({"error": "Content not found in the wishlist"}), 404

        db.session.delete(wishlist_item)

        new_transaction_log = TransactionsLog(
            user_id=current_user_id,
            action="- Wishlist",
            content_id=content_id,
            timestamp=datetime.now(),
        )
        db.session.add(new_transaction_log)

        db.session.commit()

        app.logger.info("Content Removed From Wishlist Successfully")
        return jsonify({"message": "Content removed from wishlist successfully"}), 200
    except Exception as e:
        app.logger.error("Error Removing Content From Wishlist", str(e))
        return (
            jsonify(
                {"error": "Failed to remove content from wishlist", "details": str(e)}
            ),
            500,
        )


#GET
# 1. Section
@app.route("/get-section/<int:section_id>", methods=["GET"])
@jwt_required()
def get_section(section_id):
    try:
        section = Section.query.get(section_id)

        if section:
            return jsonify({"name": section.name}), 200
        else:
            return jsonify({"error": "Section not found"}), 404
    except Exception as e:
        return jsonify({"error": "Failed to fetch section", "Reasons": str(e)}), 500
# 2. Image
def get_image_type(image_data):
    try:
        image_pil = Image.open(BytesIO(image_data))
        return image_pil.format.lower()
    except Exception as e:
        print(e)
        return None
    
# 3. PDF    
@app.route('/get_pdf/<int:content_id>')
@cache.cached(timeout=60)
@jwt_required()
def get_pdf(content_id):
    try:
        content = Content.query.get_or_404(content_id)

        pdf_blob = content.file

        pdf_bytes = BytesIO(pdf_blob)

        app.logger.info("PDF File Fetched")

        return send_file(pdf_bytes, mimetype='application/pdf', as_attachment=False)
    
    except Exception as e:
        app.logger.error("Error Fetching PDF File", str(e))
        return jsonify({"error": str(e)}), 500



#UPDATE
# 1. Section
@app.route("/update-section/<int:section_id>", methods=["PUT"])
@jwt_required()
def update_section(section_id):
    section = Section.query.get(section_id)

    data = request.get_json()
    existing_Section = Section.query.filter_by(name=data["name"]).first()
    if existing_Section:
        app.logger.warning("Section Already Exist")
        return jsonify({"error": "Section already exists"}), 400

    new_name = data.get("name")

    if not new_name:
        app.logger.error("Enter Section Name")
        return jsonify({"error": "Name is required"}), 400

    section.name = new_name
    db.session.commit()

    app.logger.info("Section Updated to: ", new_name)
    return jsonify({"message": "Section updated successfully"})

# 2. Content
@app.route("/update-content/<int:content_id>/<int:user_id>", methods=["POST"])
@jwt_required()
def update_content(content_id, user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        app.logger.warn("User Is Unauthorized")
        return jsonify({"message": "Unauthorized"}), 401

    try:
        content = Content.query.get(content_id)

        title = request.form.get("title")
        author = request.form.get("author")
        no_of_pages = request.form.get("number_of_pages")
        publish_year = request.form.get("publish_year")
        price = request.form.get("price")

        if not all([title, author, no_of_pages, publish_year]):
            app.logger.warn("Incomplete Data")
            return jsonify({"message": "Incomplete form data"}), 400

        content.title = title
        content.author = author
        content.no_of_pages = no_of_pages
        content.publish_year = publish_year
        content.price = price

        if "image" in request.files:
            image = request.files["image"]
            if image:
                filename = secure_filename(image.filename)

                image_data = image.read()

                image_type = imghdr.what(None, h=image_data)

                content.image = image_data
                content.imageType = image_type
        
        if "pdf" in request.files:
            pdf = request.files["pdf"]
            if pdf:
                filename = secure_filename(pdf.filename)
                pdf_data = pdf.read()
                try:
                    pdf_reader = PdfReader(pdf)
                    if len(pdf_reader.pages) == 0:
                        return (
                            jsonify({"message": "Invalid PDF file: No pages found"}),
                            400,
                        )
                    else:
                        content.no_of_pages = len(pdf_reader.pages)
                except Exception as e:
                    app.logger.error("Invalid PDF File")
                    return jsonify({"message": f"Invalid PDF file: {str(e)}"}), 400

                content.pdf_file_name = filename

                content.file = pdf_data

        db.session.commit()

        app.logger.info("Content Updated Successfully")
        return jsonify({"message": "Content updated successfully"}), 201

    except Exception as e:
        app.logger.error("Error Updating Content")
        return jsonify({"message": "Error updating content"}), 500











    




@app.route("/activity-data/<int:content_id>", methods=["GET"])
@jwt_required()
def get_activity_data(content_id):
    try:
        query_result = (
            db.session.query(
                Borrowing.content_id,
                Content.title,
                User.uname,
                Section.name.label("section_name"),
                Borrowing.borrow_date,
                Borrowing.returned,
                Borrowing.last_return_date,
                Borrowing.reissue_count,
                User.id.label("user_id"),
            )
            .join(User, User.id == Borrowing.member_id)
            .join(Content, Content.id == Borrowing.content_id)
            .join(Section, Section.id == Content.section)
            .filter(Borrowing.content_id == content_id, Borrowing.returned == False)
            .all()
        )

        result_data = [
            {
                "user_id": row.user_id,
                "content_id": row.content_id,
                "title": row.title,
                "username": row.uname,
                "section_name": row.section_name,
                "borrow_date": row.borrow_date.strftime("%Y-%m-%d %H:%M:%S"),
                "returned": row.returned,
                "last_return_date": (
                    row.last_return_date.strftime("%Y-%m-%d %H:%M:%S")
                    if row.last_return_date
                    else None
                ),
                "reissue_count": row.reissue_count,
                "user_id": row.user_id,
            }
            for row in query_result
        ]

        app.logger.info("Activity Data Fetched Successfully")
        return jsonify(result_data)

    except Exception as e:
        app.logger.error("Error Fetching Activity Data")
        return jsonify({"error": str(e)}), 500
    

@app.route('/current-reader-count/<int:content_id>', methods=['GET'])
@jwt_required()
def current_reader_count(content_id):
    try:
        current_count = Borrowing.query.filter_by(content_id=content_id, returned=False).distinct(Borrowing.member_id).count()
        app.logger.info("Current Reader Count Fetched")
        return jsonify({'currentReaderCount': current_count}), 200
    except Exception as e:
        app.logger.error("Error Fetching CRC", str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/total-reader-count/<int:content_id>', methods=['GET'])
@jwt_required()
def total_reader_count(content_id):
    try:
        total_count = Borrowing.query.filter_by(content_id=content_id).distinct(Borrowing.member_id).count()
        app.logger.info("Total Reader Count Fetched")
        return jsonify({'totalReaderCount': total_count}), 200
    except Exception as e:
        app.logger.error("Error Fetching TRC", str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/wishlist-count/<int:content_id>', methods=['GET'])
@jwt_required()
def wishlist_count(content_id):
    try:
        count = Wishlist.query.filter_by(content_id=content_id).count()
        app.logger.info("Wishlist Count Fetched")
        return jsonify({'wishlistCount': count}), 200
    except Exception as e:
        app.logger.error("Error Fetching WC", str(e))
        return jsonify({'error': str(e)}), 500

@app.route("/accept_request/<int:content_id>/<int:user_id>", methods=["POST"])
@jwt_required()
def accept_request(content_id, user_id):
    try:
        current_user_id = user_id

        content = Content.query.get(content_id)

        if not content:
            app.logger.warn("No Such Content Found To Borrow")
            return jsonify({"error": "Content not found"}), 404

        total_borrowing = Borrowing.query.filter_by(
            member_id=current_user_id, returned=False
        ).count()

        if total_borrowing == 5:
            app.logger.warn("Borrowing Limit Reached. Maximum 5 books can be borrowed")
            return jsonify({"error": "User has reached borrowing limit of 5."}), 400

        existing_borrowing = Borrowing.query.filter_by(
            content_id=content_id, member_id=current_user_id, return_date=None
        ).first()

        if existing_borrowing:
            app.logger.warn("Content Already Borrowed")
            return jsonify({"error": "User has already borrowed this Content"}), 400

        new_borrowing = Borrowing(
            content_id=content_id, member_id=current_user_id, borrow_date=datetime.now()
        )
        
        db.session.add(new_borrowing)

        new_borrowing.last_return_date = new_borrowing.borrow_date + timedelta(days=7)

        requests = Requests.query.filter_by(contentId=content_id, userId=user_id).first()
        if requests:
            requests.response = "Accepted"
            db.session.commit()
        else:
            app.logger.warn("Issue Request not found for the specified content and user")

        new_transaction_log = TransactionsLog(
            user_id=current_user_id,
            action="Issue",
            content_id=content_id,
            timestamp=datetime.now(),
        )

        db.session.add(new_transaction_log)

        db.session.commit()

        app.logger.info("Content Borrowed Sucessfully")
        return jsonify({"message": "Content issued successfully"}), 200
    except Exception as e:
        app.logger.error("Error Borrowing Content", str(e))
        return jsonify({"error": "Issuing content failed", "details": str(e)}), 500


@app.route("/return_content/<int:content_id>", methods=["POST"])
@jwt_required()
def return_content(content_id):
    try:
        current_user_id = get_jwt_identity()

        borrowing = Borrowing.query.filter_by(
            content_id=content_id, member_id=current_user_id, returned=False
        ).first()

        print(content_id, current_user_id, borrowing)

        if not borrowing:
            app.logger.warn("Borrowing Record Not Found / Already Returned")
            return (
                jsonify({"error": "Borrowing record not found or already returned"}),
                404,
            )

        borrowing.returned = True
        borrowing.return_date = datetime.now()
        borrowing.late = (
            borrowing.last_return_date
            and datetime.now() > borrowing.last_return_date
        )


        requests = Requests.query.filter_by(contentId=content_id, userId=current_user_id).first()
        if requests:
            db.session.delete(requests)

        new_transaction_log = TransactionsLog(
            user_id=current_user_id,
            action="Return",
            content_id=borrowing.content_id,
            timestamp=datetime.now(),
        )
        db.session.add(new_transaction_log)

        db.session.commit()

        app.logger.info("Content Returned Successfully")
        return jsonify({"message": "Content returned successfully"}), 200
    except Exception as e:
        app.logger.error("Error Returning Content", str(e))
        return jsonify({"error": "Returning content failed", "details": str(e)}), 500


@app.route("/reissue_content/<int:borrowing_id>", methods=["POST"])
@jwt_required()
def reissue_content(borrowing_id):
    try:
        current_user_id = get_jwt_identity()

        borrowing = Borrowing.query.filter_by(
            id=borrowing_id, member_id=current_user_id, return_date=None
        ).first()

        if not borrowing:
            app.logger.warn("Borrowing Record Not Found / Already Returned")
            return (
                jsonify({"error": "Borrowing record not found or already returned"}),
                404,
            )

        if borrowing.reissue_count >= 3:
            app.logger.warning("Re-Issue Limit Reached")
            return jsonify({"error": "Maximum reissue limit reached"}), 400

        borrowing.reissue_count += 1
        borrowing.estimated_return_date = borrowing.last_return_date + timedelta(days=7)
        borrowing.last_return_date = datetime.now()

        new_transaction_log = TransactionsLog(
            user_id=current_user_id,
            action="Re-Issue",
            content_id=borrowing_id,
            timestamp=datetime.now(),
        )
        db.session.add(new_transaction_log)

        db.session.commit()

        app.logger.info("Content Reissue Successful")
        return jsonify({"message": "Content reissued successfully"}), 200
    except Exception as e:
        app.logger.warn("Content Reissue Failed", str(e))
        return jsonify({"error": "Reissuing content failed", "details": str(e)}), 500






@app.route("/transaction_logs", methods=["GET"])
@jwt_required()
def get_transaction_logs():
    try:
        logs = TransactionsLog.query.all()

        serialized_logs = []
        for log in logs:
            serialized_log = {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "content_id": log.content_id,
                "timestamp": log.timestamp.isoformat(),
            }
            serialized_logs.append(serialized_log)

        app.logger.info("Transaction Logs Fetched")
        return jsonify({"transaction_logs": serialized_logs})

    except Exception as e:
        app.logger.info("Error Fetching Transaction Logs", str(e))
        return jsonify({"error": str(e)}), 500




@app.route("/revoke-access", methods=["POST"])
@jwt_required()
def revoke_access():
    data = request.get_json()

    content_id = data.get("contentId")
    user_id = data.get("userId")

    borrowing_record = Borrowing.query.filter_by(
        content_id=content_id, member_id=user_id
    ).first()

    if borrowing_record:
        borrowing_record.returned = True
        borrowing_record.return_date = datetime.now()

        requests = Requests.query.filter_by(contentId=content_id, userId=user_id).first()
        if requests:
            db.session.delete(requests)

        new_transaction_log = TransactionsLog(
            user_id=user_id,
            action="Revoke",
            content_id=content_id,
            timestamp=datetime.now(),
        )

        db.session.add(new_transaction_log)
        db.session.commit()

        app.logger.info("Access Revoked Successfully For User: %s & Content: %s", user_id, content_id)
        return jsonify({"message": "Access revoked successfully"})
    else:
        app.logger.error("Error Revoking Access")
        return jsonify({"error": "Borrowing record not found"}), 404
    

@app.route('/rate_content/<int:content_id>', methods=['POST'])
@jwt_required()
def rate_content(content_id):
    try:
        data = request.json
        rating_value = data.get('rating')
        comment = data.get('comment')

        user_id = get_jwt_identity()

        rating = Review.query.filter_by(content_id=content_id, user_id=user_id).first()
        new_transaction_log = TransactionsLog(
                user_id=user_id,
                action="New Content Review",
                content_id=content_id,
                timestamp=datetime.now(),
            )

        db.session.add(new_transaction_log)
        db.session.commit()
        
        if rating:
            rating.rating = rating_value
            rating.comment = comment

            new_transaction_log = TransactionsLog(
                user_id=user_id,
                action="Updated Content Review",
                content_id=content_id,
                timestamp=datetime.now(),
            )

            db.session.add(new_transaction_log)
            db.session.commit()
        else:
            rating = Review(content_id=content_id, user_id=user_id, rating=rating_value, comment=comment)
            db.session.add(rating)

        db.session.commit()

        app.logger.info("Content Review Saved Successfully")
        return jsonify({'message': 'Review saved successfully'}), 200
    except Exception as e:
        app.logger.info("Error Saving Content Review")
        return jsonify({'error': str(e)}), 500


@app.route('/get_previous_rating/<int:content_id>', methods=['GET'])
@jwt_required()
def get_previous_rating(content_id):
    try:
        user_id = get_jwt_identity()

        previous_rating = Review.query.filter_by(content_id=content_id, user_id=user_id).first()

        if previous_rating:
            app.logger.info("Previous Rating Fetched")
            return jsonify({
                'rating': previous_rating.rating,
                'comment': previous_rating.comment
            }), 200
        else:
            app.logger.warn("No Previous Rating Found")
            return jsonify({
                'rating': None,
                'comment': None
            }), 200
    except Exception as e:
        app.logger.error("Error Fetching Previous User Rating")
        return jsonify({'error': str(e)}), 500
    

@app.route('/reader_count_per_section', methods=['GET'])
@jwt_required()
def reader_count_per_section():
    reader_counts_per_section = db.session.query(
        Section.name,
        func.count(distinct(User.id))
    ).join(Content, Content.section == Section.id).join(Borrowing, Borrowing.content_id == Content.id).join(User).filter(
        Borrowing.returned == False
    ).group_by(Section.name).all()

    section_names = [row[0] for row in reader_counts_per_section]
    reader_counts = [row[1] for row in reader_counts_per_section]

    plt.bar(section_names, reader_counts)
    plt.xlabel('Section')
    plt.ylabel('Reader Count')
    plt.title('Reader Count Per Section')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('reader_count_per_section.png')
    plt.close()

    app.logger.info("Section Based Reader Count Chart Fetched")
    return send_file('reader_count_per_section.png', mimetype='image/png')


@app.route('/user_count_gender', methods=['GET'])
@jwt_required()
def user_count_gender_chart():
    
    male_count = User.query.filter_by(gender='male').count()
    female_count = User.query.filter_by(gender='female').count()

    if np.isnan(male_count) or np.isnan(female_count):
        app.logger.warn("Invalid Data For Pie Chart")
        return "Error: Invalid data for pie chart"

    labels = ['Male', 'Female']
    counts = [male_count, female_count]

    plt.figure(figsize=(8, 8))
    plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Male vs Female Users')

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    plt.clf()
    plt.close()

    app.logger.info("Gender Based Reader Count Chart Fetched")
    return send_file(buffer, mimetype='image/png')
    

@app.route('/search-result', methods=['GET'])
@jwt_required(optional=True)
def search_result():
    query = request.args.get('query')

    current_user_id = get_jwt_identity()

    content_results = Content.query.filter(Content.title.ilike(f'%{query}%')).all()

    formatted_content_results = []
    for content in content_results:
        image_data = content.image
        image_base64 = None
        if image_data:
            image_base64 = base64.b64encode(image_data).decode('utf-8')

        is_issued = False
        is_read = False
        is_requested = False
        is_wishlisted = False
        if current_user_id:
            borrowing = Borrowing.query.filter_by(content_id=content.id, member_id=current_user_id, returned=False).first()
            if borrowing:
                is_issued = True

            wishlist_item = Wishlist.query.filter_by(content_id=content.id, user_id=current_user_id).first()
            if wishlist_item:
                is_wishlisted = True

            read = Borrowing.query.filter_by(content_id=content.id, member_id=current_user_id, returned=False).first()
            if read:
                is_read = True

            issueRequest =Requests.query.filter_by(contentId=content.id, userId=current_user_id, response='Pending').first()
            if issueRequest:
                is_requested = True

        result = {
            'id': content.id,
            'title': content.title,
            'author': content.author,
            'section': content.section,
            'rating': db.session.query(func.avg(Review.rating)).filter(Review.content_id == content.id).scalar(),
            'imageType': content.imageType,
            'image': image_base64,
            'isRead': is_read,
            'isIssued': is_issued,
            'isWishlisted': is_wishlisted,
            'isRequested': is_requested
        }

        formatted_content_results.append(result)

    app.logger.info("Search Result Fetched")
    return jsonify({'results': formatted_content_results})


@app.route('/wishlist/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_wishlist(user_id):
    try:
        current_user_id = get_jwt_identity()
        
        wishlist_items = Wishlist.query.filter_by(user_id=user_id).all()
        wishlist = []

        for item in wishlist_items:
            content = Content.query.get(item.content_id)

            image_data = content.image
            image_base64 = base64.b64encode(image_data).decode('utf-8') if image_data else None

            is_read = False
            if current_user_id:
                borrowing = Borrowing.query.filter_by(content_id=content.id, member_id=current_user_id).first()
                is_read = bool(borrowing)

            is_wishlisted = False
            if current_user_id:
                wishlist_item = Wishlist.query.filter_by(user_id=current_user_id, content_id=content.id).first()
                is_wishlisted = bool(wishlist_item)

            is_issued = False
            if current_user_id:
                issued = Borrowing.query.filter_by(member_id=current_user_id, content_id=content.id, returned=False).first()
                is_issued = bool(issued)

            is_requested = False
            if current_user_id:
                request = Requests.query.filter_by(contentId=content.id, userId=current_user_id, response='Pending').first()
                is_requested = bool(request)

            wishlist.append({
                'id': content.id,
                'title': content.title,
                'author': content.author,
                'image': image_base64,
                'number_of_pages': content.no_of_pages,
                'publish_year': content.publish_year,
                'isRead': is_read,
                'isIssued': is_issued,
                'isWishlisted': is_wishlisted,
                'isRequested': is_requested
            })

        app.logger.info("User Wishlist Fetched")
        return jsonify({'wishlist': wishlist}), 200
    except Exception as e:
        app.logger.error("Error Fetching User Wishlist: %s", str(e))
        return jsonify({'error': str(e)}), 500
    
@app.route('/fetch_requests', methods=['GET'])
@jwt_required()
def get_requests():
    try:
        requests = Requests.query.filter_by(response='Pending').all()
        app.logger.info("Issue Requests Fetched")
        return jsonify([{'contentId': ir.contentId, 'userId': ir.userId} for ir in requests]), 200
    except Exception as e:
        app.logger.error("Error Fetching Issue Requests")
        return jsonify({'error': str(e)}), 500
    

@app.route('/user/<int:user_id>', methods=['GET'])
@cache.cached(timeout=60)
@jwt_required()
def get_user_details(user_id):
    try:
        user = User.query.get(user_id)

        if not user:
            app.logger.warn("No User Found For Fetching User Details")
            return jsonify({'error': 'User not found'}), 404

        user_details = {
            'id': user.id,
            'firstname': user.fname,
            'lastname': user.lname,
            'username': user.uname,
            'phoneNumber': user.phNumber,
            'email': user.email,
            'gender': user.gender,
            'address': user.address,
            'city': user.city,
            'state': user.state,
            'zip': user.pin,
            'role': user.role
        }

        app.logger.info("User Details Fetched")
        return jsonify(user_details), 200
    except Exception as e:
        app.logger.error("Error Fetching User Details")
        return jsonify({'error': str(e)}), 500

def getUserFromToken(token):
    try:
        decoded_token = decode_token(token)
        user_id = decoded_token['identity']
        role = decoded_token['role']
        uname = decoded_token['username']
        email = decoded_token['email']
        
        app.logger.info("User Fetched From -> Token Decoded")
        return {'id': user_id, 'role': role, 'username': uname, 'email': email}
    except Exception as e:
        app.logger.error("Error Decoding Token", str(e))
        return None


@app.route('/create_request/<int:contentId>', methods=['POST'])
@jwt_required()
def create_requests(contentId):
    try:
        current_user_id = get_jwt_identity()
        
        existing_requests = Requests.query.filter(
        Requests.contentId == contentId,
        Requests.userId == current_user_id,
        Requests.response != 'Accepted'
        ).first()
        
        if existing_requests:
            app.logger.warn("Issue Request Already Present")
            return jsonify({'message': 'Issue request already exists'}), 400


        new_requests = Requests(contentId=contentId, userId=current_user_id)
        db.session.add(new_requests)
        db.session.commit()
        
        app.logger.info("Issue Request Created")
        return jsonify({'message': 'Issue request created successfully'}), 201
    except Exception as e:
        app.logger.error("Error Creating Request")
        return jsonify({'error': str(e)}), 500
    



@app.route('/detail_view/<int:content_id>/<int:user_id>', methods=["GET"])
@jwt_required()
def detailed_view(content_id, user_id):
    try:
        user = User.query.get(user_id)
        content = Content.query.get(content_id)
        
        if user is None or content is None:
            return jsonify({'error': 'User or content not found'}), 404

        response_data = {
            'username': user.uname,
            'contentName': content.title,
            'sectionName': Section.query.get(content.section).name
        }
        
        app.logger.info("Details fetched successfully")
        return jsonify(response_data), 200
    except Exception as e:
        app.logger.error("Error fetching details: %s", str(e))
        return jsonify({'error': 'Error fetching details'}), 500    


@app.route("/reject_request/<int:content_id>/<int:user_id>", methods=["GET", "POST"])
@jwt_required()
def reject_request(content_id, user_id):
    try:
        requests = Requests.query.filter_by(contentId=content_id, userId=user_id).first()
        if requests:
            requests.response = "Rejected"
            db.session.commit()
            return jsonify({"message": "Issue request rejected successfully"}), 200
        else:
            app.logger.warn("Issue Request not found for the specified content and user")
            return jsonify({"error": "Issue request not found"}), 404
    except Exception as e:
        app.logger.error("Error rejecting issue request", str(e))
        return jsonify({"error": "Rejecting issue request failed", "details": str(e)}), 500

@app.route('/download_purchase/<int:contentId>', methods=['GET'])
@jwt_required()
def download_purchase(contentId):

    current_user_id = get_jwt_identity()

    content = Content.query.get(contentId)
    if content is None:
        return abort(404, description="Content not found")

    content_amount = content.price

    pdf_blob = content.file

    pdf_bytes = BytesIO(pdf_blob)

    purchase_data = Purchase.query.filter_by(user_id=current_user_id, content_id=contentId).first()
    if purchase_data:

        new_transaction_log = TransactionsLog(
            user_id=current_user_id,
            action="Re-Download",
            content_id=contentId,
            timestamp=datetime.now(),
        )

        db.session.add(new_transaction_log)

        db.session.commit()
        app.logger.info("PDF File Sent For Download - Already Paid")
        return send_file(pdf_bytes, as_attachment=True, mimetype='application/pdf', download_name="Book.pdf")
    
    if (purchase_data == None):
        user = User.query.get(current_user_id)
        if user.balance_amt < content.price:
            app.logger.warn("Insufficient Account balance_amt")
            return abort(400, description="Insufficient balance_amt to purchase content")

        user.balance_amt -= content.price
        new_purchase = Purchase(user_id = current_user_id, content_id = contentId, amount=content_amount)
        db.session.add(new_purchase)
        db.session.commit()

        new_transaction_log = TransactionsLog(
            user_id=current_user_id,
            action="Bought",
            content_id=contentId,
            timestamp=datetime.now(),
        )

        db.session.add(new_transaction_log)

        db.session.commit()

        app.logger.info("PDF File Sent For Download - Paid Now")
        return send_file(pdf_bytes, as_attachment=True, mimetype='application/pdf', download_name="Book.pdf")

    app.logger.error("Error Purchasing Content")
    return abort(403, description="Content not purchased")



class NotFoundError(HTTPException):
    def __init__(self, status_code):
        self.response = make_response("", status_code)

class CourseNameError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {"error_code": error_code, "error_message": error_message}
        self.response = make_response(json.dumps(message), status_code)


book_parser = reqparse.RequestParser()
book_parser.add_argument("title")
book_parser.add_argument("author")
book_parser.add_argument("publish_year")
book_parser.add_argument("no_of_pages")
book_parser.add_argument("price")
book_parser.add_argument("section_id")

user_parser = reqparse.RequestParser()
user_parser.add_argument("fname")
user_parser.add_argument("lname")
user_parser.add_argument("uname")
user_parser.add_argument("email")
user_parser.add_argument("password")
user_parser.add_argument("role")
user_parser.add_argument("balance_amt")

review_parser = reqparse.RequestParser()
review_parser.add_argument("rating")
review_parser.add_argument("comment")
review_parser.add_argument("content_id")
review_parser.add_argument("user_id")



class BookApi(Resource):
    def get(self, id):
        entry = Content.query.get(id)
        if entry:
            jsonobj = {
                "book_id": entry.id,
                "title": entry.title,
                "author": entry.author,
                "publish_year": entry.publish_year,
                "no_of_pages": entry.no_of_pages,
                "price": entry.price,
                "section_id": entry.section,
            }
            return jsonobj
        else:
            raise NotFoundError(status_code=404)
        
    def post(self):
        args = book_parser.parse_args()
        title_u = args.get("title", None)
        author_u = args.get("author", None)
        publish_year_u = args.get("publish_year", None)
        no_of_pages_u = args.get("no_of_pages", None)
        price_u = args.get("price", None)
        section_id_u = args.get("section_id", None)
        if not all([title_u, author_u, publish_year_u, no_of_pages_u, price_u, section_id_u]):
            raise CourseNameError(status_code=400, error_code="BOOK_ERROR", error_message="Sufficient data not found")

        entry = Content.query.filter_by(title=title_u).first()
        if entry:
            return "Book already exists", 409

        entry = Content(title=title_u, author=author_u, publish_year=publish_year_u, no_of_pages=no_of_pages_u, price=price_u, section=section_id_u,image=None,imageType=None, file=None,pdf_file_name=None )
        db.session.add(entry)
        db.session.commit()
        jsonobj = {
            "book_id": entry.id,
            "title": entry.title,
            "author": entry.author,
            "publish_year": entry.publish_year,
            "no_of_pages": entry.no_of_pages,
            "price": entry.price,
            "section_id": entry.section,
        }
        return jsonobj, 201

    def put(self, id):
        entry = Content.query.get(id)
        if not entry:
            raise NotFoundError(status_code=404)
        
        args = book_parser.parse_args()
        title_u = args.get("title", None)
        author_u = args.get("author", None)
        publish_year_u = args.get("publish_year", None)
        no_of_pages_u = args.get("no_of_pages", None)
        price_u = args.get("price", None)
        section_id_u = args.get("section_id", None)
        if not all([title_u, author_u, publish_year_u, no_of_pages_u, price_u, section_id_u]):
            raise CourseNameError(status_code=400, error_code="BOOK_ERROR", error_message="Sufficient data not found")

        entry.title = title_u
        entry.author = author_u
        entry.publish_year = publish_year_u
        entry.no_of_pages = no_of_pages_u
        entry.price = price_u
        entry.section = section_id_u
        db.session.commit()
        jsonobj = {
            "book_id": entry.id,
            "title": entry.title,
            "author": entry.author,
            "publish_year": entry.publish_year,
            "no_of_pages": entry.no_of_pages,
            "price": entry.price,
            "section_id": entry.section,
        }
        return jsonobj, 200


    def delete(self, id):
        entry = Content.query.get(id)
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return "Successfully Deleted", 200
        else:
            raise NotFoundError(status_code=404)

class UserApi(Resource):
    def get(self, id):
        entry = User.query.get(id)
        if entry:
            jsonobj = {
                "user_id": entry.id,
                "fname": entry.fname,
                "lname": entry.lname,
                "uname": entry.uname,
                "email": entry.email,
                "role": entry.role,
                "balance_amt": entry.balance_amt,
            }
            return jsonobj
        else:
            raise NotFoundError(status_code=404)

    def post(self):
        args = user_parser.parse_args()
        fname_u = args.get("fname", None)
        lname_u = args.get("lname", None)
        uname_u = args.get("uname", None)
        email_u = args.get("email", None)
        password_u = args.get("password", None)
        role_u = args.get("role", None)
        balance_amt_u = args.get("balance_amt", None)
        if not all([fname_u, lname_u, uname_u, email_u, password_u, role_u]):
            raise CourseNameError(status_code=400, error_code="USER_ERROR", error_message="Sufficient data not found")

        entry = User.query.filter_by(email=email_u).first()
        if entry:
            return "User already exists", 409

        new_user = User(
            fname=fname_u,
            lname=lname_u,
            uname=uname_u,
            email=email_u,
            password=password_u,
            role=role_u,
            balance_amt=balance_amt_u if balance_amt_u else 1000.0,
        )
        db.session.add(new_user)
        db.session.commit()
        jsonobj = {
            "user_id": new_user.id,
            "fname": new_user.fname,
            "lname": new_user.lname,
            "uname": new_user.uname,
            "email": new_user.email,
            "role": new_user.role,
            "balance_amt": new_user.balance_amt,
        }
        return jsonobj, 201

    def put(self, id):
        entry = User.query.get(id)
        if not entry:
            raise NotFoundError(status_code=404)
        
        args = user_parser.parse_args()
        fname_u = args.get("fname", None)
        lname_u = args.get("lname", None)
        uname_u = args.get("uname", None)
        email_u = args.get("email", None)
        password_u = args.get("password", None)
        role_u = args.get("role", None)
        balance_amt_u = args.get("balance_amt", None)
        if not all([fname_u, lname_u, uname_u, email_u, password_u, role_u]):
            raise CourseNameError(status_code=400, error_code="USER_ERROR", error_message="Sufficient data not found")

        entry.fname = fname_u
        entry.lname = lname_u
        entry.uname = uname_u
        entry.email = email_u
        entry.password = password_u
        entry.role = role_u
        entry.balance_amt = balance_amt_u if balance_amt_u else entry.balance_amt
        db.session.commit()
        jsonobj = {
            "user_id": entry.id,
            "fname": entry.fname,
            "lname": entry.lname,
            "uname": entry.uname,
            "email": entry.email,
            "role": entry.role,
            "balance_amt": entry.balance_amt,
        }
        return jsonobj, 200

    def delete(self, id):
        entry = User.query.get(id)
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return "Successfully Deleted", 200
        else:
            raise NotFoundError(status_code=404)


class ReviewApi(Resource):
    def get(self, id):
        entry = Review.query.get(id)
        if entry:
            jsonobj = {
                "review_id": entry.id,
                "rating": entry.rating,
                "comment": entry.comment,
                "content_id": entry.content_id,
                "user_id": entry.user_id,
            }
            return jsonobj
        else:
            raise NotFoundError(status_code=404)

    def post(self):
        args = review_parser.parse_args()
        rating_u = args.get("rating", None)
        comment_u = args.get("comment", None)
        content_id_u = args.get("content_id", None)
        user_id_u = args.get("user_id", None)
        if not all([rating_u, comment_u, content_id_u, user_id_u]):
            raise CourseNameError(status_code=400, error_code="REVIEW_ERROR", error_message="Sufficient data not found")

        new_review = Review(
            rating=rating_u,
            comment=comment_u,
            content_id=content_id_u,
            user_id=user_id_u,
        )
        db.session.add(new_review)
        db.session.commit()
        jsonobj = {
            "review_id": new_review.id,
            "rating": new_review.rating,
            "comment": new_review.comment,
            "content_id": new_review.content_id,
            "user_id": new_review.user_id,
        }
        return jsonobj, 201

    def put(self, id):
        entry = Review.query.get(id)
        if not entry:
            raise NotFoundError(status_code=404)
        
        args = review_parser.parse_args()
        rating_u = args.get("rating", None)
        comment_u = args.get("comment", None)
        if not all([rating_u, comment_u]):
            raise CourseNameError(status_code=400, error_code="REVIEW_ERROR", error_message="Sufficient data not found")

        entry.rating = rating_u
        entry.comment = comment_u
        db.session.commit()
        jsonobj = {
            "review_id": entry.id,
            "rating": entry.rating,
            "comment": entry.comment,
            "content_id": entry.content_id,
            "user_id": entry.user_id,
        }
        return jsonobj, 200

    def delete(self, id):
        entry = Review.query.get(id)
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return "Successfully Deleted", 200
        else:
            raise NotFoundError(status_code=404)


api.add_resource(BookApi, "/api/book/<int:id>", "/api/book")
api.add_resource(UserApi, "/api/user/<int:id>", "/api/user")
api.add_resource(ReviewApi, "/api/review/<int:id>", "/api/review")




if __name__ == "__main__":
    with app.app_context():
        print("Creating all tables...")
        
        db.create_all()
        print("Tables created successfully.")
    app.run(debug=True)