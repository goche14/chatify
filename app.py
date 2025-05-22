from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from forms import loginform
from models import post
from models import user

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatify.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/')
def home():
    posts = post.query.order_by(post.id.desc()).all()
    return render_template('index.html', title='Chatify', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = loginform()
    if form.validate_on_submit():
        return f"Welcome, {form.username.data}!"
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = user.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check username and password', 'danger')
    
    return render_template('login.html', title='Login - Chatify')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = loginform()
    if form.validate_on_submit():
        return f"Welcome, {form.username.data}!"
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        existing_user = user.query.filter_by(username=username).first()
        
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = user(username=username, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register - Chatify')

@app.route('/post', methods=['POST'])
def post():
    if 'user_id' not in session:
        flash('Please log in to post', 'danger')
        return redirect(url_for('login'))
    
    content = request.form['content']
    
    if not content:
        flash('Post cannot be empty', 'danger')
        return redirect(url_for('home'))
    
    new_post = post(content=content, user_id=session['user_id'])
    db.session.add(new_post)
    db.session.commit()
    
    flash('Your post has been created!', 'success')
    return redirect(url_for('home'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)