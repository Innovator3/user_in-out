from flask import Blueprint, request, render_template, redirect, flash, url_for, session
from db.mongo import users_collection

signup_blueprint = Blueprint('signup', __name__, url_prefix='/signup')

@signup_blueprint.route('/', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        
        # Validation
        if not all([name, email, password, confirm]):
            flash('Please fill in all fields', 'error')
            return redirect(url_for('signup.signup'))
            
        if password != confirm:
            flash('Passwords do not match', 'error')
            return redirect(url_for('signup.signup'))
            
        if users_collection.find_one({'email': email}):
            flash('Email already registered', 'error')
            return redirect(url_for('signup.signup'))
            
        # Insert new user
        users_collection.insert_one({
            'name': name,
            'email': email,
            'password': password  # Note: In production, hash the password!
        })
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login.login'))
        
    return render_template("signup.html")