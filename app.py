from flask import Flask, render_template, request, redirect, flash
import mysql.connector
from mysql.connector import Error
import logging
import re
from config import DB_CONFIG, SECRET_KEY  # Import database configuration and secret key

# Initialize Flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY  # Use the secret key from environment variables

# Configure logging for error tracking
logging.basicConfig(
    level=logging.ERROR,
    filename="app.log",  # Log file to store error details
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Define the maximum length for the 'name' field
MAX_NAME_LENGTH = 50


def is_valid_name(name):
    """
    Validates the name input based on specific rules.

    Validation Rules:
    1. Name cannot be empty or contain only spaces.
    2. Name cannot be a number or consist only of numeric characters.
    3. Name length must not exceed the defined MAX_NAME_LENGTH.
    4. Name cannot contain special characters such as $^&*%%(.
    5. Name must contain only letters, numbers, and spaces.

    Parameters:
    name (str): The input name to validate.

    Returns:
    Tuple (bool, str): True and None if valid, False and error message otherwise.
    """
    if not name or not name.strip():
        return False, "Name cannot be empty."
    
    # Remove leading and trailing whitespace
    name = name.strip()
    
    # Check if the name is purely numeric
    if name.isdigit():
        return False, "Name cannot be a number."
    
    # Check if the name exceeds the maximum length
    if len(name) > MAX_NAME_LENGTH:
        return False, f"Name cannot be longer than {MAX_NAME_LENGTH} characters."
    
    # Check for special characters using a regex
    if re.search(r'[^\w\s]', name):  # Matches any character that is not a word or whitespace
        return False, "Name cannot contain special characters like $^&*%%(."
    
    return True, None


def get_user_by_name(name):
    """
    Queries the database to check if a user with the given name already exists.

    Parameters:
    name (str): The name to search in the database.

    Returns:
    dict or None: A dictionary containing user data if found, otherwise None.
    """
    try:
        # Connect to the database using credentials from DB_CONFIG
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # Query to search for the user by name
        query = "SELECT * FROM users WHERE name = %s"
        cursor.execute(query, (name,))
        user = cursor.fetchone()  # Fetch the first matching result

        # Close database cursor and connection
        cursor.close()
        conn.close()

        return user
    except Error as e:
        logging.error(f"Database error occurred: {e}")  # Log database errors
        return None


def add_user_to_db(name):
    """
    Adds a new user to the database.

    Parameters:
    name (str): The name of the user to add.

    Returns:
    bool: True if the user was successfully added, False otherwise.
    """
    try:
        # Connect to the database using credentials from DB_CONFIG
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Query to insert the user into the database
        query = "INSERT INTO users (name) VALUES (%s)"
        cursor.execute(query, (name,))
        conn.commit()  # Commit the transaction to save changes

        # Close database cursor and connection
        cursor.close()
        conn.close()

        return True  # User was successfully added
    except mysql.connector.IntegrityError:
        logging.error("Duplicate entry error: The user already exists.")
        return False
    except Error as e:
        logging.error(f"Database error occurred while inserting user: {e}")
        return False


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Home route to display the form and handle form submissions.

    For GET requests:
    - Render the HTML form.

    For POST requests:
    - Validate the user's name.
    - Check if the user already exists in the database.
    - Add the user to the database if they do not already exist.
    - Display appropriate flash messages for success or failure.

    Returns:
    str: Rendered HTML template.
    """
    if request.method == "POST":
        # Retrieve the user's input from the form
        name = request.form.get("name")

        # Validate the input name
        is_valid, error_message = is_valid_name(name)
        if not is_valid:
            flash(error_message, "error")  # Show validation error
            return redirect("/")  # Redirect to the homepage

        name = name.strip()  # Remove leading/trailing whitespace

        # Check if the user already exists in the database
        user = get_user_by_name(name)
        if user:
            flash("User already exists.", "error")  # Notify the user
            return redirect("/")
        
        # Add the user to the database
        if add_user_to_db(name):
            flash("User added successfully.", "success")
        else:
            flash("Failed to add user. Please try again.", "error")
        
        return redirect("/")

    # Render the form template for GET requests
    return render_template("index.html")


if __name__ == "__main__":
    """
    Main entry point for running the Flask app.
    """
    app.run(debug=True)
