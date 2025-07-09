from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'replace-this-with-a-secure-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Note model
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    notes = Note.query.filter_by(user_id=user.id).all()
    return render_template('dashboard.html', notes=notes, username=user.username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
def add_note():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    content = request.form['content']
    new_note = Note(content=content, user_id=session['user_id'])
    db.session.add(new_note)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:note_id>')
def delete_note(note_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    note = Note.query.get(note_id)
    if note and note.user_id == session['user_id']:
        db.session.delete(note)
        db.session.commit()
    return redirect(url_for('index'))

# ✅ Initialization (Flask 3.x compatible)
def initialize_app():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('password')
            db.session.add(admin)
            db.session.commit()

initialize_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
