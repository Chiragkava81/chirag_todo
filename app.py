from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "mysecretkey"

#Database Setup
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


IST = timezone(timedelta(hours=5, minutes=30))
class TodoItem(db.Model):

    srno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(IST))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self) -> str:
        return f"{self.srno} - {self.title}"
    
# AUTH Routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please login.", "danger")
            return redirect(url_for("login"))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Signup successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop("user_id", None)
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))



@app.route('/', methods=['GET', 'POST'])
def home():
    if "user_id" not in session:
        flash("Please login to access your ToDos", "warning")
        return redirect(url_for("login"))
    
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')
        todo = TodoItem(title=title, desc=desc, user_id=session["user_id"])
        db.session.add(todo)
        db.session.commit()
        flash("Todo added successfully!", "success")

    all_todos = TodoItem.query.filter_by(user_id=session["user_id"]).all()

    return render_template('index.html', all_todos=all_todos)

@app.route('/delete/<int:srno>')
def delete_todo(srno):
    if "user_id" not in session:
        return redirect(url_for("login"))

    todo = TodoItem.query.filter_by(srno=srno, user_id=session["user_id"]).first()
    if todo:
        db.session.delete(todo)
        db.session.commit()
        flash("Todo deleted", "info")
    else:
        flash("Not authorized to delete this todo", "danger")

    return redirect(url_for("home"))

@app.route('/edit/<int:srno>', methods=['GET', 'POST'])
def update_todo(srno):
    if "user_id" not in session:
        return redirect(url_for("login"))

    todo = TodoItem.query.filter_by(srno=srno, user_id=session["user_id"]).first()
    if not todo:
        flash("Not authorized to edit this todo", "danger")
        return redirect(url_for("home"))

    if request.method == 'POST':
        todo.title = request.form.get('title')
        todo.desc = request.form.get('desc')
        db.session.commit()
        flash("Todo updated!", "success")
        return redirect(url_for('home'))

    return render_template('edit.html', todo=todo)


# RUN APP
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)