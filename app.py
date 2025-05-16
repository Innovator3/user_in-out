from flask import Flask, render_template, session, redirect, url_for, flash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__, static_folder='static')
app.secret_key = os.getenv("SECRET_KEY")

# Configure session
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Should be True in production with HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=3600  # 1 hour
)

from auth.login import login_blueprint
from auth.signup import signup_blueprint
from auth.google_auth import google_blueprint

app.register_blueprint(login_blueprint)
app.register_blueprint(signup_blueprint)
app.register_blueprint(google_blueprint)

@app.route('/')
def home():
    if 'username' in session:
        return render_template("welcome.html", username=session['username'])
    return redirect(url_for('login.login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('email', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login.login'))

if __name__ == '__main__':
    app.run(debug=True)