from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from forms import loginform
from models import post, user
from app import db  

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def home():
    posts = post.query.order_by(post.id.desc()).all()
    return render_template('index.html', title='Chatify', posts=posts)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = loginform()
    if form.validate_on_submit():
        return f"Welcome, {form.username.data}!"
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        found_user = user.query.filter_by(username=username).first()
        
        if found_user and check_password_hash(found_user.password, password):
            session['user_id'] = found_user.id
            session['username'] = found_user.username
            flash('Login successful!', 'success')
            return redirect(url_for('main_bp.home'))
        else:
            flash('Login unsuccessful. Please check username and password', 'danger')
    
    return render_template('login.html', title='Login - Chatify')

@main_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('main_bp.home'))

@main_bp.route('/register', methods=['GET', 'POST'])
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
            return redirect(url_for('main_bp.register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = user(username=username, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('main_bp.login'))
    
    return render_template('register.html', title='Register - Chatify')

@main_bp.route('/post', methods=['POST'])
def create_post():
    if 'user_id' not in session:
        flash('Please log in to post', 'danger')
        return redirect(url_for('main_bp.login'))
    
    content = request.form['content']
    
    if not content:
        flash('Post cannot be empty', 'danger')
        return redirect(url_for('main_bp.home'))
    
    new_post = post(content=content, user_id=session['user_id'])
    db.session.add(new_post)
    db.session.commit()
    
    flash('Your post has been created!', 'success')
    return redirect(url_for('main_bp.home'))
