from flask import Blueprint, redirect, url_for, session, request, flash
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os
from dotenv import load_dotenv
from db.mongo import users_collection

load_dotenv()

google_blueprint = Blueprint('google_auth', __name__, url_prefix='/google')

# Allow HTTP for development (remove in production)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")  # Must match exactly

def create_google_flow():
    return Flow.from_client_config(
        client_config={
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ],
        redirect_uri=REDIRECT_URI
    )

@google_blueprint.route('/login')
def google_login():
    if 'username' in session:
        return redirect(url_for('home'))
        
    flow = create_google_flow()
    authorization_url, state = flow.authorization_url(
        prompt='consent',
        access_type='offline',
        include_granted_scopes='true'
    )
    session['oauth_state'] = state  # Store state in session
    return redirect(authorization_url)

@google_blueprint.route('/callback')
def google_callback():
    if 'username' in session:
        return redirect(url_for('home'))
        
    if 'oauth_state' not in session:
        flash('Invalid OAuth state', 'error')
        return redirect(url_for('login.login'))
    
    flow = create_google_flow()
    
    try:
        flow.fetch_token(authorization_response=request.url)
        
        # Verify state matches
        if session['oauth_state'] != request.args.get('state'):
            flash('Invalid state parameter', 'error')
            return redirect(url_for('login.login'))
            
        credentials = flow.credentials
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
        
        # Check if user exists in DB
        user = users_collection.find_one({'email': id_info.get('email')})
        
        if not user:
            # Create new user if doesn't exist
            users_collection.insert_one({
                'name': id_info.get('name'),
                'email': id_info.get('email'),
                'password': None  # No password for Google auth users
            })
        
        # Set session variables
        session['username'] = id_info.get('name')
        session['email'] = id_info.get('email')
        session.pop('oauth_state', None)  # Clean up session
        flash('Logged in successfully with Google!', 'success')
        return redirect(url_for('home'))
        
    except Exception as e:
        print(f"Google auth error: {str(e)}")  # Debugging
        flash('Google authentication failed', 'error')
        return redirect(url_for('login.login'))