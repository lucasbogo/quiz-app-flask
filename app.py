from flask import Flask, render_template, url_for, request, redirect, session, g
from database import Database
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()

def get_current_user():
    user_result = None # global variable set to none 
    if 'user' in session:
        user = session['user'] # get user from session and store in variable
        db = Database().connect() # connect to database
        user_cursor = db.execute("SELECT * FROM users WHERE name = ?", [user]) # execute query to check if user exists in the database
        user_result = user_cursor.fetchone() # fetch the result of the query 

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        db = Database().connect()
        name = request.form['name']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')

        db.execute("INSERT INTO users (name, password, teacher, admin) VALUES (?, ?, ?, ?)", [name, hashed_password, '0', '0'])
        db.connection.commit()
        return redirect(url_for('index'))

    return render_template("register.html")

@app.route("/logout")
def logout():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)
