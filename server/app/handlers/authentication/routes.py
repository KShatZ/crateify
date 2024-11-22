from flask import request, redirect
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from field_names import HTTP, SPOTIFY
from ...models.user import User
from ...helpers.spotify.spotify_api import SpotifyAPI
from ...helpers.spotify.spotify_auth import SpotifyAuth
from ...helpers.response import create_response

from . import Authentication as bp

#
# ------ Auth Check Routes ------ #
#
@bp.get("/auth/validate")
@login_required
def is_authorized():
    # NOTE: Potentially include checks that the logged-in user is the one 
    # that is requesting the protected route. Flask-Login might already 
    # be handling this.

    # Check for Spotify Tokens
    if current_user.tokens is None:
        print(f"GET:/auth/validate --- User({current_user.id}) --- User is missing spotify tokens, redirecting to Spotify oAuth page.")
        data = {"redirect_url": SpotifyAuth.spotify_oauth_url()}
        return create_response(data=data, status_code=HTTP.SEE_OTHER)

    print(f"GET:/auth/validate --- User({current_user.id}) --- Authorized!")
    data = {"username": current_user.username} # Might include more in the future
    return create_response(data=data)



#
# ------ Spotify oAuth Flow Routes ------ #
#
@bp.post("/auth/spotify/token-exchange")
@login_required
def request_spotify_user_tokens():

    request_body = request.json

    # TODO: Decide what to do on error
    # User either did not accept oAuth, or error occured
    if request_body.get("error"):
        return create_response(error=True, msg="Got an error and no code", status_code=500)

    code = request_body.get("code")
    # state = request_params.get("state") # TODO - Need to incorporate state somehow
    
    # TODO: Handle when no code in response. User gave permision, but
    # spotify did not give code, probably need to retry the oAuth flow.
    if not code:
        return create_response(error=True, msg="Got no code", status_code=500)

    try:
        user_auth_tokens = SpotifyAuth.request_auth_tokens(code)
        
        updated = current_user.update_spotify_tokens(user_auth_tokens)
        if not updated:
            # TODO: What to do
            return create_response(error=True, msg="Failed to update user tokens", status_code=500)
    except:
        # TODO: What to do
        return create_response(error=True, msg="Failed to exchange tokens", status_code=500)

    # NOTE: Depending on how we handle reauthentication in the future, this profile part might not be done here
    # Get user's spotify profile and populate
    spotify_api = SpotifyAPI(current_user)
    response = spotify_api.send_request(endpoint="/me")

    if response["status_code"] != HTTP.OK:
        # TODO
        print(f"request_spotify_user_tokens() --- There was an issue hitting the /me endpoint")
        return create_response()

    # Populate User's profile
    try:
        populated = current_user.populate_spotify_profile(response["data"])
    except Exception as e:
        # TODO
        print(f"request_spotify_user_tokens() --- Issue populating user spotify profile --- {e}")

    if not populated:
        # TODO: Think about this
        # I think it's okay to keep on going with this, and have the profile checked with the /auth route and handle
        # population if need be. 
        print(f"request_spotify_user_tokens() --- Issue populating user spotify profile")

    return create_response()


#
# ------ Register Routes ------ #
#
@bp.post("/register")
def post_register():
    
    user_creds = request.get_json()

    # TODO: Input validation - ensure proper user/pass sent
    # TODO: Sanitize user credentials before sending to DB
    username = user_creds.get("username")

    try:
        if (User.user_exists(username)):
            # - Log - # 
            # TODO: Security Concern - Change to email flow later on
            error_msg = "Username not available, try again with different username." 
            return create_response(error=True, msg=error_msg, status_code=HTTP.CONFLICT)
        
        user_id = User.create(user_creds)
    except Exception:
        error_msg = "Server Error: Please try again, there was an issue creating your account."
        return create_response(error=True, msg=error_msg, status_code=HTTP.SERVER_ERROR)

    if not user_id:
        # - Log - #
        error_msg = "Server Error: Please try again, there was an issue creating your account."
        return create_response(error=True, msg=error_msg, status_code=HTTP.SERVER_ERROR)
    
    # - Log - # 
    print(f"New User Created: {username}") 
    return create_response(status_code=HTTP.CREATED)


#
# ------ Login Routes ------ #
#
@bp.post("/login")
def post_login():

    # TODO: Sanitize credentials and ensure they were sent
    user_creds = request.get_json()
    username = user_creds.get("username")
    password = user_creds.get("password")

    try:
        user = User.get_user(username=username, password=True)
    except Exception:
        error_msg = "Server Error: Please try again, there was an issue logging you in."
        return create_response(error=True, msg=error_msg, status_code=HTTP.SERVER_ERROR)  

    if not user:
        # TODO - What to do on incorrect username
        # - Log - #
        print(f"POST /login --- Invalid username [{username}] provided")
        error_msg = "Login Failed: Invalid username and/or password, please try again."
        return create_response(error=True, msg=error_msg, status_code=HTTP.BAD_REQUEST)

    if not check_password_hash(user.password, password):
        # TODO - What to do on incorrect password
        # - Log - #
        print(f"POST /login --- Invalid password for username: {username} provided")
        error_msg = "Login Failed: Invalid username and/or password, please try again."
        return create_response(error=True, msg=error_msg, status_code=HTTP.BAD_REQUEST)

    # Log the user in
    if login_user(user): 
        # TODO: Logging when user logs in
        # - Log - #
        print(f"POST /login --- Logged in user {username} succesfully.")
        return create_response()
    else:
        error_msg = "Server Error: Please try again, there was an issue logging you in."
        return create_response(error=True, msg=error_msg, status_code=HTTP.SERVER_ERROR)


#
# ------ Logout Route ------ #
#
@bp.post("/logout")
@login_required
def logout():
    # - Log - #
    print(f"logout -- Username: {current_user.username} _id: {current_user.id}")
    logout_user()
    return create_response(msg="OK")
