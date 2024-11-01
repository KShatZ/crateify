from flask import request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from field_names import HTTP, SPOTIFY
from . import Authentication as bp
from ...models.user import User
from .helpers.user import user_exists, create_user, get_user, update_spotify_object
from .helpers.spotify import obtain_tokens, get_user_spotify_profile
from ...helpers.response import create_response


#
# ------ Auth Session Check Routes ------ #
#
@bp.get("/auth/user")
@login_required
def get_auth_user():
    
    # Current user is missing spotify object - Redirect to Spotify oAuth page for authorization
    if current_user.spotify_profile is None:
        # - Log - # 
        print(f"/auth/user -- Session authenticated but {current_user.username} missing spotify object.")
        
        data = {"redirect_uri": SPOTIFY.oauth_url()}
        return create_response(error=False, data=data, status_code=HTTP.SEE_OTHER)

    # - Log - #
    print(f"/auth/user -- Session for '{current_user.username}' authorized")
    return create_response(status_code=HTTP.OK, data=current_user.current_user)


#
# ------ Spotify oAuth Routes ------ #
#
@bp.post("/auth/spotify/tokens")
@login_required
def post_spotify_tokens():

    data = request.get_json()
    code = data.get("code", None)

    if not code:
        # - Log - #
        msg = "Code was missing in the request."
        return create_response(error=True, msg=msg, status_code=HTTP.BAD_REQUEST)
        
    tokens = obtain_tokens(code)
    tokens["profile"] = get_user_spotify_profile(tokens.get("access_token"))
    
    try: 
        result = update_spotify_object(tokens, current_user.id)

        if not result:
            # TODO: What to do if update fails? 
            return create_response(error=True, msg="TODO: Not Developed", status_code=HTTP.SERVER_ERROR)
        
        return create_response(msg="Tokens updated", status_code=HTTP.OK)

    except Exception as e: 
        # - Log - #
        print("post_spotify_tokens: Error in updating users spotify object", e)

        msg = "Error updating tokens"
        return create_response(error=True, msg=msg, status_code=HTTP.SERVER_ERROR)
    

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
