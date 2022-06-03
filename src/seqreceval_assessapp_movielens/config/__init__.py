# Flask
SECRET_KEY = "development"

# Flask-SQLAlchemy
SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# App-specific
SEQRECEVAL_ASSESSAPP_CONDITIONS = [
    (10, False),
    (20, True)
]
SEQRECEVAL_ASSESSAPP_ASSESSMENT_COUNT = 3