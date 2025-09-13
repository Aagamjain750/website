from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import hashlib
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # production me env variable use karna

# ---------- Database Setup ----------
conn = sqlite3.connect("project_portal.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_description TEXT,
    phone_number TEXT,
    email TEXT,
    language TEXT,
    username TEXT
)
""")
conn.commit()

# ---------- Helper Functions ----------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

# ---------- Routes ----------
@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                           (username, hash_password(password)))
            conn.commit()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return render_template("register.html", alert="⚠️ Username already exists!")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        if user and verify_password(password, user[0]):
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", alert="⚠️ Invalid username or password!")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    cursor.execute("SELECT * FROM projects WHERE username=?", (session["username"],))
    projects = cursor.fetchall()

    return render_template("dashboard.html", username=session["username"], projects=projects)

@app.route("/submit_project", methods=["GET", "POST"])
def submit_project():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        project_description = request.form["project_description"]
        phone_number = request.form["phone_number"]
        email = request.form["email"]
        language = request.form["language"]

        cursor.execute("INSERT INTO projects (project_description, phone_number, email, language, username) VALUES (?, ?, ?, ?, ?)",
                       (project_description, phone_number, email, language, session["username"]))
        conn.commit()

        return redirect(url_for("projects"))

    return render_template("submit_project.html")

@app.route("/projects")
def projects():
    if "username" not in session:
        return redirect(url_for("login"))

    cursor.execute("SELECT * FROM projects")
    all_projects = cursor.fetchall()

    return render_template("projects.html", projects=all_projects)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

# ---------- Run App ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
