from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class TodoItem(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"{self.srno} - {self.title}"
    
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')
        todo = TodoItem(title=title, desc=desc)
        db.session.add(todo)
        db.session.commit()

    all_todos = TodoItem.query.all()

    return render_template('index.html', all_todos=all_todos)

@app.route('/delete/<int:srno>')
def delete_todo(srno):
    todo = TodoItem.query.filter_by(srno=srno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect('/')

@app.route('/edit/<int:srno>', methods=['GET', 'POST'])
def update_todo(srno):
    todo = TodoItem.query.get(srno)
    if request.method == 'POST':
        todo.title = request.form.get('title')
        todo.desc = request.form.get('desc')
        db.session.commit()
        return redirect('/')
    
    return render_template('edit.html', todo=todo)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)