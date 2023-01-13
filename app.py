from flask import Flask, render_template, url_for, request, redirect, session, g
from database import DbConnection
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
        db = DbConnection().get_connection()
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
        db = DbConnection().get_connection()
        name = request.form['name']
        password = request.form['password']
        # execute query to check if user exists in the database
        user_fetching_cursor = db.execute(
            "SELECT * FROM users WHERE name = ?", [name])
        existing_user = user_fetching_cursor.fetchone()

        if existing_user:  # check if user exists
            # check if password is correct
            if check_password_hash(existing_user[2], password):
                session['user'] = existing_user[1]  # set session user to name
                return redirect(url_for('index'))
            else:
                error = "Invalid password"  # return error message if password is wrong
        else:
            error = "User does not exist"   # return error message if user does not exist

    return render_template("login.html", user=user, error=error)


@app.route('/register', methods=["POST", "GET"])
def register():
    user = get_current_user()
    error = None
    if request.method == "POST":
        db = DbConnection().get_connection()
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


@app.route("/ask", methods=["POST", "GET"])
def ask():
    user = get_current_user()
    db = DbConnection().get_connection()
    if request.method == "POST":
        question = request.form['question']
        teacher = request.form['teacher']
        db.execute("INSERT INTO questions (question, user_id, teacher_id) VALUES (?, ?, ?)", [
                   question, user[0], teacher])
        db.connection.commit()
        return redirect(url_for('index'))
    teacher_cursor = db.execute("SELECT * FROM users WHERE teacher = 1")
    teachers = teacher_cursor.fetchall()
    return render_template("ask.html", user=user, teachers=teachers)

@app.route("/questions", methods=["POST", "GET"])
def questions():
    user = get_current_user()
    db = DbConnection().get_connection()
    question_cursor = db.execute(
        "select questions.id, questions.question, users.name from questions join users on users.id = questions.user_id where questions.answer IS NULL and questions.teacher_id = ?", [user[0]])
    questions = question_cursor.fetchall()
    return render_template("questions.html", user=user, questions=questions)

@app.route("/answer<question_id>", methods=["POST", "GET"])
def answer(question_id):
    user = get_current_user()
    db = DbConnection().get_connection()
    question_cursor = db.execute(
        "select question from questions where id = ?", [question_id])
    question = question_cursor.fetchall()
    return render_template("answer.html", user=user, question_id=question_id, question=question)


@app.route("/users", methods=["POST", "GET"])
def users():
    user = get_current_user()
    db = DbConnection().get_connection()
    user_cursor = db.execute("SELECT * FROM users")
    users = user_cursor.fetchall()
    return render_template("users.html", user=user, users=users)


@app.route("/promote/<int:id>", methods=["POST", "GET"])
def promote(id):
    user = get_current_user()
    if request.method == "GET":
        db = DbConnection().get_connection()
        db.execute("UPDATE users SET teacher = 1 WHERE id = ?", [id])
        db.connection.commit()
        return redirect(url_for('users', user=user))
    return render_template("users.html", user=user)


@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
