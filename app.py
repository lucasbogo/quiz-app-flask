from flask import Flask, render_template, url_for, request, redirect, session, g
from database import Database
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
# generate a random key for the session with 24 caracters
app.config['SECRET_KEY'] = os.urandom(24)

# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()


def get_current_user():
    user_result = None  # global variable set to none
    if 'user' in session:
        user = session['user']  # get user from session and store in variable
        db = Database().connect()  # connect to database
        # execute query to check if user exists in the database
        user_cursor = db.execute("SELECT * FROM users WHERE name = ?", [user])
        user_result = user_cursor.fetchone()  # fetch the result of the query
    return user_result  # return the result


@app.route("/")
def index():
    user = get_current_user()  # get the current user
    return render_template("home.html", user=user)


@app.route("/login", methods=["POST", "GET"])
def login():
    user = get_current_user()
    error = None
    if request.method == "POST":
        db = Database().connect()
        name = request.form['name']
        password = request.form['password']

        # execute query to check if user exists in the database
        user_fetching_cursor = db.execute(
            "SELECT * FROM users WHERE name = ?", [name])
        existing_user = user_fetching_cursor.fetchone()

        if existing_user:
            if check_password_hash(existing_user[2], password):
                session['user'] = existing_user[1]
                return redirect(url_for('index'))
            else:
                error = "Username or password is incorrect"
                # return render_template("login.html", error=error)
        else:
            error = "Username or password is incorrect"
            # return redirect(url_for('login'))

    return render_template("login.html", user=user, error=error)


@app.route('/register', methods=["POST", "GET"])
def register():
    user = get_current_user()
    error = None
    if request.method == "POST":
        db = Database().connect()
        name = request.form['name']
        password = request.form['password']

        # execute query to check if user exists in the database
        user_fetching_cursor = db.execute(
            "SELECT * FROM users WHERE name = ?", [name])
        existing_user = user_fetching_cursor.fetchone()  # fetch the result of the query
        # check if user exists
        if existing_user:
            error = "User already exists"
            # return error message if user exists and render the register page again
            return render_template("register.html", error=error)

        hashed_password = generate_password_hash(password, method='sha256')
        db.execute("INSERT INTO users (name, password, teacher, admin) VALUES (?, ?, ?, ?)", [
                   name, hashed_password, '0', '0'])
        db.connection.commit()
        session['user'] = name  # set session user to name
        return redirect(url_for('index'))

    return render_template("register.html", user=user)


@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
