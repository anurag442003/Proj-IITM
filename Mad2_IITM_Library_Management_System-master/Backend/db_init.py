from Mad2_app import app, db

with app.app_context():
    print("Creating all tables...")
    db.create_all()
    print("Tables created successfully.")
