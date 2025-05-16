from flask import Blueprint, request, render_template, redirect, session, flash, url_for
from db.mongo import users_collection

login_blueprint = Blueprint('login', __name__, url_prefix='/login')

@login_blueprint.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please fill in all fields', 'error')
            return redirect(url_for('login.login'))
            
        user = users_collection.find_one({'email': email, 'password': password})
        
        if user:
            session['username'] = user['name']
            session['email'] = user['email']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
            
        flash('Invalid email or password', 'error')
        return redirect(url_for('login.login'))
        
    return render_template("login.html")