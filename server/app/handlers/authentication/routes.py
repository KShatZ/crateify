from flask import request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from field_names import HTTP, SPOTIFY
from . import Authentication as bp
from ...models.user import User
from ...helpers.spotify.spotify_auth import SpotifyAuth
from .helpers.user import user_exists, create_user, get_user, update_spotify_object
from .helpers.spotify import obtain_tokens, get_user_spotify_profile
from ...helpers.response import create_response


#
# ------ Auth Session Check Routes ------ #
#
@bp.get("/auth/user") # Should be something like /auth/validate_user
@login_required
def get_auth_user():
    
    # Current user is missing spotify object - Redirect to Spotify oAuth page for authorization
    if current_user.spotify_profile is None:
        # - Log - # 
        print(f"/auth/user -- Session authenticated but {current_user.username} missing spotify object.")
        
        # data = {"redirect_uri": SPOTIFY.oauth_url()}
        data = {"redirect_uri": SpotifyAuth.spotify_oauth_url()}
        return create_response(error=False, data=data, status_code=HTTP.SEE_OTHER)

    # - Log - #
    print(f"/auth/user -- Session for '{current_user.username}' authorized")
    return create_response(status_code=HTTP.OK, data=current_user.current_user)


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


    # TODO: Get and Populate User Spotify Profile
    
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
        if (user_exists(username=username)):
            # - Log - # 
            # TODO: Security Concern - Change to email flow later on
            error_msg = "Username not available, try again with different username." 
            return create_response(error=True, msg=error_msg, status_code=HTTP.CONFLICT)
        
        user_id = create_user(user_creds)
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
        user_doc = get_user(username=username)
    except Exception:
        error_msg = "Server Error: Please try again, there was an issue logging you in."
        return create_response(error=True, msg=error_msg, status_code=HTTP.SERVER_ERROR)  

    # The username provided does not exist
    # The password provided is incorrect
    if not user_doc or not check_password_hash(user_doc["password"], password):
        # - Log - #
        error_msg = "Login Failed: Invalid username and/or password, please try again."
        return create_response(error=True, msg=error_msg, status_code=HTTP.BAD_REQUEST)
    
    # Log the user in
    if login_user(User(user_doc)): 

        # - Log - #
        print(f"User Login - Username: {username}")

        # # User did not grant Spotify oAuth
        # if not user_doc["spotify"]:
        #     # TODO: Need to handle how to redirect to spotify auth
        #     # - Log - #
        #     print(f"Spotify oAuth Missing - Username: {username}")
        #     pass
        
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
