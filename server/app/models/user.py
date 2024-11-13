from urllib.parse import urlparse, parse_qsl

from bson import ObjectId
from flask_login import UserMixin
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

from ..helpers.spotify_api import SpotifyAPI
from ..helpers.spotify.spotify_auth import SpotifyAuth
from field_names import DB

class User(UserMixin):

    def __init__(self, user_doc):
        self.id = str(user_doc.get("_id"))
        self.username = user_doc.get("username")
        self.password = user_doc.get("password") 

        if user_doc.get("spotify", None) and user_doc["spotify"] != {}:
            self.tokens = {
                "access": user_doc["spotify"].get("access_token"),
                "refresh": user_doc["spotify"].get("refresh_token")
            }
            self.spotify_profile = user_doc["spotify"].get("profile")
        else:
            self.tokens = None
            self.spotify_profile = None


    @classmethod
    def create(cls, user_credentials):
        """Inserts new user doc to the users collection, thus creating a new user. 
        Assumes that the username provided with the user credentials does not 
        already exist in the collection.

        :param user_credentials: The credentials provided during registration.
        :type user_credentials: dict
        :return: The _id of the newly created user doc
        :rtype: ObjectId
        """

        # TODO: Mongo Single Instance
        mongo = MongoClient(host=DB.MONGO_URI)
        users_collection = mongo[DB.DB][DB.USERS_COLLECTION]

        user = {
            "username": user_credentials["username"],
            "password": generate_password_hash(user_credentials["password"]),
            "spotify": {}
        }
        try:
            result = users_collection.insert_one(user)
            mongo.close()
        except Exception as MongoError:
            # TODO: What to do on error
            # -- Log -- #
            print(f"create() --- Error inserting new user: {user['username']} --- {MongoError}")
            return None
        
        return result.inserted_id


    @classmethod
    def user_exists(cls, username): # Potentially could include the _id if ever needed as param
        """Queries mongo user collection to see if a user with given username already exists.

        :param username: Crateify user username
        :type username: string
        :return: Whether or not the user with given username already exsits
        :rtype: bool
        """

        # TODO: Mongo Single Instance
        mongo = MongoClient(host=DB.MONGO_URI)
        users_collection = mongo[DB.DB][DB.USERS_COLLECTION]

        try: 
            user = users_collection.find_one({"username": username}, {"_id": 1})
            mongo.close()
        except Exception as MongoError:
            # TODO: What to do on error
            # -- Log -- #
            print(f"user_exists() --- Encountered error while querying for user: {username} --- {MongoError}")
            return False

        if user:
            return True
        return False
    
    
    @classmethod
    def get_user(cls, user_id=None, username=None, password=False):
        """Queries the mongo user collection for a user doc that matches the `user_id`
        or `username` provided. If both are provided, the user_id is prioritized for
        the query over the username. 

        By default the user doc that is found does not contain the hashed password of
        the user. Must explicitly set `password` to True, if password is needed.

        :param user_id: The _id of the user document, defaults to None
        :type user_id: string, optional
        :param username: The users' crateify username, defaults to None
        :type username: string, optional
        :param password: Whether or not to include the password field in
        the returned user document, defaults to False
        :type password: bool, optional
        :raises ValueError: If neither `user_id` or `username` are passed then the query
        cant be run.
        :return: The mongo user doc.
        :rtype: dict
        """

        if user_id is None and username is None:
            # TODO: What to do when neither provided
            print("get_user() --- Can't get user, need to have _id or username provided...")
            raise ValueError("Either _id or usernmae must be provided")

        query = {}
        proj = {} if password else {"password": 0}

        if user_id is not None:
            query["_id"] = ObjectId(str(user_id))
        elif username is not None:
            query["username"] = username

        # TODO: Mongo Single Instance
        mongo = MongoClient(host=DB.MONGO_URI)
        users_collection = mongo[DB.DB][DB.USERS_COLLECTION]

        try:
            user = users_collection.find_one(query, proj)
            mongo.close()
        except Exception as MongoError:
            # TODO: What to do one error
            # -- Log -- #
            print(f"get_user() --- Error while querying for user with _id: {user_id} username: {username} --- {MongoError}")

        if not user:
            return None
                
        return cls(user)


    @property
    def spotify_follower_count(self):
        """Returns spotify follower count of the current User instance, 
        found within the spotify_profile dict.

        :return: The total number of spotify followers the User has, or
        None if doesn't exist.
        :rtype: int
        """

        if not self.spotify_profile:
            return None

        return self.spotify_profile["followers"].get("total", None)
    
    
    @property
    def spotify_following_count(self):

        endpoint = "/me/following"
        params = {"type": "artist", "limit": 1}

        request = SpotifyAPI(self.id, endpoint=endpoint, params=params)
        
        if not request.send():
            # TODO: At the moment, this only happens if there are too many
            # requests, or oAuth issue on our apps end.
            return "N/A - Error"

        return request.response_data["artists"].get("total", "N/A - Error")


    @property
    def spotify_profile_image(self):
        """Returns the largest spotify profile picture of current User 
        instance from the spotify_profile dict.

        :return: The url to the largest spotify profile picture found in 
        spotify_profile dict, or empty string if none found
        :rtype: str
        """

        images = self.spotify_profile.get("images", [])

        max_width = 0
        biggest_image = None

        for i, image in enumerate(images):
            image_width = image.get("width", 0)

            if image_width > max_width:
                max_width = image_width
                biggest_image = i

        if not biggest_image:
            return ""
        
        return images[biggest_image].get("url", "")


    @property
    def current_user(self):
        """Returns a user dictionary containing keys with values pertianing
        to the current User instance. This dictionary is meant to be sent to
        the client as part of the response in the authentication handler with
        endpoint /auth/user. This dict returned is used as the currentUser 
        client side.

        :return: A user dict containing values pertaining to the current User instance,
        to be used client side.
        :rtype: dict
        """
  
        user = {
            "username": self.username,
            "spotify_profile": {
                "profile_url": self.spotify_profile["external_urls"].get("spotify"),
                "profile_type": self.spotify_profile.get("type", "user"),
                "display_name": self.spotify_profile.get("display_name"),
                "profile_image": self.spotify_profile_image,
                "follower_count": self.spotify_follower_count,
                "following_count": self.spotify_following_count,
            }
        }

        return user
    

    def update_spotify_tokens(self, user_auth_tokens):
        """Updates spotify auth tokens with the user doc. This function is intended
        to be used on registration, as well as when refreshing tokens due to the way 
        `tokens_to_update` is populated. Whatever is provided to the function is what
        gets updated.

        :param user_auth_tokens: Tokens received from Spotify's token route, whether on
        initial exchange or during token refresh. May contain the access token, the 
        refresh token, as well as scope. 
        :type user_auth_tokens: dict
        :return: Whether updating the user's document was succesful or not.
        :rtype: bool
        """

        # TODO: Mongo Single Instance
        mongo = MongoClient(host=DB.MONGO_URI)
        users_collection = mongo[DB.DB][DB.USERS_COLLECTION]

        tokens_to_update = {f"spotify.tokens.{key}": value for key, value in user_auth_tokens.items()}
        try: 
            result = users_collection.update_one(
                {"_id": ObjectId(self.id)}, 
                {"$set": tokens_to_update}
            )

            mongo.close()

            # TODO: Logging, and error handling for the 'Falses'
            if result.matched_count == 1:
                if result.modified_count == 1:
                    print(f"update_spotify_tokens() --- Spotify Tokens for _id: {self.id} were updated")
                    return True
                else:
                    print(f"update_spotify_tokens() --- Spotify Tokens for _id {self.id} were not updated")
                    return False
            else:
                print(f"update_spotify_tokens() --- No document matched for _id: {self.id}")
                return False

        # TODO: What to do if mongo operation has exception
        except Exception as error:
            print("The error:", error)
            return False


    def get_spotify_playlists(self):
        """Sends a request to Spotify playlists endpoint to retrieve metadata on
        all the playlists owned by this user. Specifically the playlist spotify id,
        name, image, public status, and track count.

        :return: A list of dicts (playlists)
        :rtype: dict
        """

        user_playlists = []
        user_spotify_id = self.spotify_profile.get("id")

        endpoint = "/me/playlists"
        params = {
            "limit": 50 # TODO - Env Var?
        }
        
        request = SpotifyAPI(self.id, endpoint=endpoint, params=params)

        done = False
        while not done:

            if not request.send():
                # TODO: In the case that the request has an issue
                return None
            
            playlists = request.response_data.get("items")
            for playlist in playlists:

                # Only get playlists directly owned by user
                owner_id = playlist["owner"].get("id")
                if owner_id != user_spotify_id:
                    continue

                playlist_images = playlist.get("images", [])
                if not playlist_images:
                    # No image associated with playlist
                    image = None
                else:
                    # First image is the biggest in size - Spotify Docs
                    image = playlist_images[0].get("url")
                
                user_playlists.append({
                    "id": playlist.get("id"),
                    "name": playlist.get("name"),
                    "image": image,
                    "public": playlist.get("public"),
                    "track_count": playlist["tracks"].get("total"),
                    "snapshot_id": playlist.get("snapshot_id"),
                })

            api_next_url = request.response_data.get("next")
            if api_next_url:
                parsed_next_url = urlparse(api_next_url)                
                # Retrieve the params for next page of playlists
                next_params = parse_qsl(parsed_next_url.query)
                for key, value in next_params:
                    request.params[key] = value
            else:
                done = True

        return user_playlists
