import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# Local database URL (replace with own)
SQLALCHEMY_DATABASE_URI = 'postgresql://fyyur:fyyur@localhost:5432/fyyur'
