import os
import sqlite3
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__, static_folder="static")
UPLOAD_DIR = "user_uploads"
app.config["UPLOAD_DIR"] = UPLOAD_DIR

# Ensure upload folder exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Database Configuration
DB_FILE = "database.sqlite"

def initialize_database():
    """Create the users table if it doesn't exist."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                user_password TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                user_email TEXT NOT NULL,
                uploaded_file_path TEXT,
                total_words INTEGER DEFAULT 0
            )
        """)
        conn.commit()

initialize_database()  # Initialize DB on startup

@app.route("/")
def index():
    return render_template("signup.html")

@app.route("/signup", methods=["POST"])
def signup():
    username = request.form.get("username")
    user_password = request.form.get("password")
    first_name = request.form.get("firstname")
    last_name = request.form.get("lastname")
    user_email = request.form.get("email")

    # Handle File Upload
    uploaded_file = request.files.get("file")
    uploaded_file_path = None
    total_words = 0

    if uploaded_file and uploaded_file.filename:
        uploaded_file_path = os.path.join(app.config["UPLOAD_DIR"], uploaded_file.filename)
        uploaded_file.save(uploaded_file_path)

        # Count words in the uploaded file
        with open(uploaded_file_path, "r") as file:
            total_words = len(file.read().split())

    # Insert user data into the database
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, user_password, first_name, last_name, user_email, uploaded_file_path, total_words)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, user_password, first_name, last_name, user_email, uploaded_file_path, total_words))
        conn.commit()

    return redirect(url_for("user_profile", username=username))

@app.route("/user/<username>")
def user_profile(username):
    """Fetch and display user profile information."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user_data = cursor.fetchone()

    if user_data:
        return render_template("profile_page.html", user=user_data)
    else:
        return "User not found", 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)