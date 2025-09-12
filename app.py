from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Apna secret key

# ---------- Database Connection ----------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Aagam@123",  # Apna MySQL password
    database="project_portal"
)
cursor = db.cursor(dictionary=True)

# ---------- Root Route ----------
@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("main"))
    return redirect(url_for("login"))

# ---------- Signup ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            return render_template("signup.html", alert="⚠️ Username already exists!")

        # Insert user
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        return redirect(url_for("login"))

    return render_template("signup.html")

# ---------- Login ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        if user:
            session["username"] = username
            return redirect(url_for("main"))
        else:
            return render_template("login.html", alert="⚠️ Login failed! Invalid username or password.")

    return render_template("login.html")

# ---------- Main Page ----------
@app.route("/main")
def main():
    if "username" not in session:
        return redirect(url_for("login"))

    # Last selected language
    cursor.execute("SELECT language FROM project_contacts WHERE username=%s ORDER BY id DESC LIMIT 1", (session["username"],))
    last = cursor.fetchone()
    last_language = last["language"] if last else None

    return render_template("main.html", username=session["username"], last_language=last_language)

# ---------- Project Form ----------
@app.route("/project_form", methods=["GET", "POST"])
def project_form():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        project_description = request.form["project_description"]
        phone_number = request.form["phone_number"]
        language = request.form["language"]

        # Insert project with username and language
        cursor.execute(
            "INSERT INTO project_contacts (project_description, phone_number, email, language, username) VALUES (%s, %s, %s, %s, %s)",
            (project_description, phone_number, "N/A", language, session["username"])
        )
        db.commit()
        return render_template("project_submited.html", language=language)

    return render_template("project_form.html")

# ---------- Logout ----------
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
