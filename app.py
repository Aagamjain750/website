from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change in production

# ---------- Database Connection ----------
conn = sqlite3.connect("project_portal.db", check_same_thread=False)
cursor = conn.cursor()

# Create tables if not exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS project_contacts (
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
        return redirect(url_for("main"))
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
            conn.commit()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return render_template("signup.html", alert="⚠️ Username already exists!")
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        if user and verify_password(password, user[0]):
            session["username"] = username
            return redirect(url_for("main"))
        else:
            return render_template("login.html", alert="⚠️ Login failed! Invalid username or password.")
    return render_template("login.html")

@app.route("/main")
def main():
    if "username" not in session:
        return redirect(url_for("login"))
    cursor.execute("SELECT language FROM project_contacts WHERE username=? ORDER BY id DESC LIMIT 1", (session["username"],))
    last = cursor.fetchone()
    last_language = last[0] if last else None
    return render_template("main.html", username=session["username"], last_language=last_language)

@app.route("/project_form", methods=["GET", "POST"])
def project_form():
    if "username" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        project_description = request.form["project_description"]
        phone_number = request.form["phone_number"]
        email = request.form.get("email", "N/A")
        language = request.form["language"]
        cursor.execute("INSERT INTO project_contacts (project_description, phone_number, email, language, username) VALUES (?, ?, ?, ?, ?)",
                       (project_description, phone_number, email, language, session["username"]))
        conn.commit()
        return render_template("project_submited.html", language=language)
    return render_template("project_form.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
