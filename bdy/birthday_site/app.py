from datetime import datetime
import os
import sqlitecloud
import smtplib
from email.mime.text import MIMEText

from flask import Flask, g, redirect, render_template, request, session, url_for


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = "birthday-site-secret-key"
DEFAULT_USERNAME = "birthday"
DEFAULT_PASSWORD = "surprise123"
TARGET_BIRTHDAY = "2026-12-31 00:00:00"

# SQLite Cloud connection string
SQLITECLOUD_URL = "sqlitecloud://cqmi27ahvz.g1.sqlite.cloud:8860/auth.sqlitecloud?apikey=68YHWVUrrEiaBFOMxPLq7klsnQ9YhDLNSESQc5HpmLc"

# Email configuration
SENDER_EMAIL = "yourgmail@gmail.com"
RECEIVER_EMAIL = "yourgmail@gmail.com"
EMAIL_PASSWORD = "your_app_password"


app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["TARGET_BIRTHDAY"] = TARGET_BIRTHDAY


def get_db():
    if "db" not in g:
        g.db = sqlitecloud.connect(SQLITECLOUD_URL)
        g.db.row_factory = sqlitecloud.Row
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Initialize the database - creates users table if it doesn't exist"""
    db = sqlitecloud.connect(SQLITECLOUD_URL)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        """
    )
    # Check if default user exists
    user = db.execute(
        "SELECT id FROM users WHERE username = ?", (DEFAULT_USERNAME,)
    ).fetchone()
    if user is None:
        db.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (DEFAULT_USERNAME, DEFAULT_PASSWORD),
        )
    db.commit()
    db.close()


def is_logged_in():
    return "user_id" in session


@app.route("/", methods=["GET", "POST"])
def login():
    if is_logged_in():
        return redirect(url_for("dashboard"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = get_db().execute(
            "SELECT id, username FROM users WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        error = "Incorrect username or password."

    return render_template(
        "login.html",
        error=error,
        default_username=DEFAULT_USERNAME,
        default_password=DEFAULT_PASSWORD,
    )


@app.route("/dashboard")
def dashboard():
    if not is_logged_in():
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session.get("username"))


@app.route("/countdown")
def countdown():
    if not is_logged_in():
        return redirect(url_for("login"))
    return render_template("countdown.html", target_birthday=app.config["TARGET_BIRTHDAY"])


@app.route("/slideshow")
def slideshow():
    if not is_logged_in():
        return redirect(url_for("login"))
    slides = [
        {
            "image": url_for("static", filename="images/img1.jpg"),
            "caption": "Every birthday memory deserves a spotlight.",
        },
        {
            "image": url_for("static", filename="images/img2.jpg"),
            "caption": "Replace the placeholder files with your favorite photos.",
        },
    ]
    return render_template("slideshow.html", slides=slides)


@app.route("/wishes")
def wishes():
    if not is_logged_in():
        return redirect(url_for("login"))
    notes = [
        "Wishing you a day filled with laughter, cake, and unforgettable memories.",
        "May this year bring you new adventures, kind people, and quiet moments of joy.",
        "You deserve to feel celebrated not just today, but every day.",
    ]
    return render_template("wishes.html", notes=notes)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/send_message", methods=["POST"])
def send_message():
    if not is_logged_in():
        return redirect(url_for("login"))
    
    message = request.form.get("message", "").strip()
    
    if message:
        try:
            msg = MIMEText(message)
            msg["Subject"] = "Birthday Message Received"
            msg["From"] = SENDER_EMAIL
            msg["To"] = RECEIVER_EMAIL
            
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
            server.quit()
        except Exception as e:
            print(f"Email error: {e}")
    
    return redirect(url_for("wishes"))


# Admin route to add users (for initial setup)
@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    # Simple admin key protection
    admin_key = request.args.get("key")
    if admin_key != "admin123":
        return "Unauthorized", 403
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if username and password:
            try:
                db = get_db()
                db.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password),
                )
                db.commit()
                return f"User '{username}' created successfully!"
            except Exception:
                return "Username already exists!", 400
    
    return """
    <form method="post">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Add User</button>
    </form>
    """


init_db()


if __name__ == "__main__":
    app.run(debug=True)
