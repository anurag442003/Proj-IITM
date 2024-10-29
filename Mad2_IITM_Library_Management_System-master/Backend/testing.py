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

from Mad2_app import revoke_access, create_csv, monthly_report, deactivate_user

class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///Mad2_TheWisdom.db'
    JWT_SECRET_KEY = '22f1000362'
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


from Mad2_Models import db, User, Service, Content, Borrowing, TransactionsLog, Review, Login, Requests
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

with app.app_context():
    # Test monthly_report
    print("Testing monthly_report...")
    monthly_report()  # Call the function directly
    print("Monthly report generated.")

    # Test revoke_access
    # print("Testing revoke_access...")
    # revoke_access()  # Call the function directly
    # print("Access revoked for expired borrowings.")

    # Test delete_rejected_issue_requests
    print("Testing deactivate")
    deactivate_user()  # Call the function directly
    print("Deactivated")

    # Test create_csv
    print("Testing create_csv...")
    result = create_csv()  # Call the function directly
    print(f"CSV created at: {result.get('csv_file_path') if 'csv_file_path' in result else result.get('error')}")