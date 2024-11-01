from bson import ObjectId
from pymongo import MongoClient
from werkzeug.security import generate_password_hash


from field_names import DB

mongo = MongoClient(host=DB.MONGO_URI)
USERS_COLLECTION = mongo["spotify-visualizer"]["users"] # TODO: env vars


def user_exists(user_id="", username=None):
    """Check mongo user collection if a user exists with 
    the provided document _id or username.

    :param user_id: The _id of user doc that is being checked for, defaults to ""
    :type user_id: str, optional
    :param username: The username of user that is being checked for, defaults to None
    :type username: str, optional
    :return: True if user exists, False if user does not exist
    :rtype: bool
    """

    try:
        user = USERS_COLLECTION.find_one({"username": username} if username else \
                                    {"_id": ObjectId(user_id)})
    except Exception as MongoError:
        # - Log - #
        print(f"Error while checking if user [{user_id} / {username}] exists. --- MongoError: {MongoError}")
        raise Exception(f"MongoError while checking if user exists --> {MongoError}")

    if user:
        return True
    return False
    

def create_user(user_creds):
    """Creates a new user document and inserts it into the user collection.

    :param user_creds: The username and password to use for the new user
    to be created.
    :type user_creds: dict
    :return: The mongo _id for the newly created user, or None if there was 
    an issue inserting the user into the users collection.
    :rtype: ObjectId
    """
    
    user = {
        "username": user_creds["username"],
        "password": generate_password_hash(user_creds["password"]),
        "spotify": None
    }
    
    try:
        result = USERS_COLLECTION.insert_one(user)
    except Exception as MongoError:
        # - Log - #
        print(f"Error creating a user --> {MongoError}")
        raise Exception(f"MongoError in create_user() --> {MongoError}")
    
    return result.inserted_id


def get_user(user_id="", username=None):
    """Performs a query to the mongo 'users' collection querying
    in order to return a user doc that matches the provided
    username or user _id.

    :param user_id: _id of user to query for, defaults to ""
    :type user_id: str, optional
    :param username: username of user to query for, defaults to None
    :type username: str, optional
    :raises Exception: In the case there is an issue with querying mongo
    there is an exception raised passing the error up.
    :return: The user doc that waas queried for if it exists.
    :rtype: dict or None
    """

    try:
        user = USERS_COLLECTION.find_one({"username": username} if username else \
                                         {"_id": ObjectId(user_id)}) 
    except Exception as MongoError:
        # - Log - #
        print(f"Error getting a user --> {MongoError}")
        raise Exception(f"MongoError in get_user() --> {MongoError}")
    
    if not user:
        return None
    
    return user


def update_spotify_object(spotify, user_id):
    """Spotify oAuth helper: Updates spotify object in the user's mongo
    document. 

    :param spotify: The spotify object containing the data to be added/updated
    to users mongo doc
    :type spotify: dict
    :param user_id: The _id of the user that the spotify data belongs too
    :type user_id: str
    :raises MongoError: Any errors that occur when communicating with Mongo server.
    :return: If update was succesful or not
    :rtype: bool
    """
    try: 
        result = USERS_COLLECTION.update_one({"_id": ObjectId(user_id)}, {"$set": {"spotify": spotify}}, upsert=False)

        if result.modified_count == 0:
            # - Log - #
            print(f"update_spotify_object -- spotify object not update for user _id: {user_id}")
            return False

        return True

    except Exception as MongoError:
        # - Log - #
        print(MongoError)
        print(f"update_spotify -- Issue updating spotify for user _id:{user_id}")
        raise MongoError(f"update_spotify -- Issue updating spotify for user _id:{user_id}")
