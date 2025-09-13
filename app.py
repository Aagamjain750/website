from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "mysecret123"  # Tumhare Railway project ka strong secret

# ---------- Database Connection (Railway credentials) ----------
db = mysql.connector.connect(
    host="mysql.railway.internal",
    user="root",
    password="biMDOAICiXVKxOZspePBNrecfgYoUbju",
    database="project_portal",
    port=3306
)
cursor = db.cursor(dictionary=True)

# ---------- Root Route ----------
@app.route("/")
def index():
    if "username" in session:
        return redirect("/main")
    return redirect("/login")

# ---------- Signup ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            return render_template("signup.html", alert="⚠️ Username already exists!")

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        return redirect("/login")

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
            return redirect("/main")
        else:
            return render_template("login.html", alert="⚠️ Invalid username or password!")

    return render_template("login.html")

# ---------- Main Page ----------
@app.route("/main")
def main():
    if "username" not in session:
        return redirect("/login")

    cursor.execute(
        "SELECT language FROM project_contacts WHERE username=%s ORDER BY id DESC LIMIT 1",
        (session["username"],)
    )
    last = cursor.fetchone()
    last_language = last["language"] if last else "No language submitted"
    return render_template("main.html", username=session["username"], last_language=last_language)

# ---------- Project Form ----------
@app.route("/project_form", methods=["GET", "POST"])
def project_form():
    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":
        project_description = request.form["project_description"]
        phone_number = request.form["phone_number"]
        email = request.form.get("email", "N/A")
        language = request.form["language"]

        cursor.execute(
            "INSERT INTO project_contacts (project_description, phone_number, email, language, username) "
            "VALUES (%s, %s, %s, %s, %s)",
            (project_description, phone_number, email, language, session["username"])
        )
        db.commit()
        return render_template("project_submited.html", language=language)

    return render_template("project_form.html")

# ---------- Logout ----------
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/login")

# ---------- Run App ----------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
