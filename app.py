from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret in production

# MySQL connection (Railway credentials)
db = mysql.connector.connect(
    host='containers-us-west-180.railway.app',
    user='root',
    password='NTS3eac1vYxL9RkWzq1H',
    database='project_portal',
    port=3306
)
cursor = db.cursor()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        return redirect('/')
    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    if user:
        session['username'] = username
        return redirect('/project_form')
    return "Invalid credentials"

@app.route('/project_form', methods=['GET', 'POST'])
def project_form():
    if 'username' not in session:
        return redirect('/')
    if request.method == 'POST':
        project_description = request.form['project_description']
        phone_number = request.form['phone_number']
        email = request.form['email'] or 'N/A'
        language = request.form['language']
        username = session['username']
        cursor.execute("""
            INSERT INTO project_contacts (project_description, phone_number, email, language, username)
            VALUES (%s, %s, %s, %s, %s)
        """, (project_description, phone_number, email, language, username))
        db.commit()
        return redirect('/main')
    return render_template('project_form.html')

@app.route('/main')
def main():
    if 'username' not in session:
        return redirect('/')
    username = session['username']
    cursor.execute("SELECT language FROM project_contacts WHERE username = %s ORDER BY id DESC LIMIT 1", (username,))
    result = cursor.fetchone()
    language = result[0] if result else "No language submitted"
    return render_template('main.html', language=language)

if __name__ == '__main__':
    app.run(debug=True)