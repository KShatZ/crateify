from flask_login import LoginManager

from field_names import HTTP
from ..helpers.response import create_response
from ..handlers.authentication.helpers.user import get_user
from ..models.user import User


login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    """Queries mongo for user in order to load into session.
    Runs on each request and is a required flask-login function.

    :param user_id: The mongo Object ID of a user
    :type user_id: str
    :return: If the user_id exsists, returns User object. None, otherwise.
    :rtype: User
    """ 

    try: 
        user_doc = get_user(user_id=user_id)
    except Exception:
        # - Log - #
        print("load_user -- Error in getting user with get_user(), mongo error most likely.")
        return None
    
    return User(user_doc) if user_doc else None
        

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
