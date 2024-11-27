import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# Flask secret key
SECRET_KEY = os.getenv('SECRET_KEY')
