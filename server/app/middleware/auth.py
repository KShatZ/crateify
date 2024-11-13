from flask_login import LoginManager

from field_names import HTTP
from ..helpers.response import create_response
from ..models.user import User


login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    """Queries mongo for user in order to load into session.
    Runs on each request and is a required flask-login function.

    :param user_id: Mongo _id of user.
    :type user_id: str
    :return: If the user_id exsists, returns User object. None, otherwise.
    :rtype: User
    """ 

    try: 
        user = User.get_user(user_id=user_id)
    except Exception as e:
        # TODO: What to do if error
        # - Log - #
        print(f"load_user() --- There was an issue loading user with _id: {user_id} --- {e}")
    
    if not user:
        return None
    
    return user
        

@login_manager.unauthorized_handler
def unauthorized():
    """Handles requests that fail the @login_required check 
    on specific routes by sending back a 401 Unauthorized
    response.

    This is a custom implementation of Flask-Login's 
    unauthorized() callback.

    :return: 401 UNAUTHORIZED response
    :rtype: Flask Response object
    """

    print("unathoroized -- Inside unauthorized handler...")

    return create_response(msg="UNAUTHORIZED", error=True, status_code=HTTP.UNAUTHORIZED)
