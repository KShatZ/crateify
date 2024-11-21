from urllib.parse import urlparse, parse_qsl
from typing import Optional

from bson import ObjectId
from flask_login import UserMixin
import requests
from pymongo import MongoClient
from werkzeug.security import generate_password_hash


# from ..helpers.spotify_api import SpotifyAPI
from ..helpers.spotify.spotify_api import SpotifyAPI
from ..helpers.spotify.spotify_auth import SpotifyAuth
from field_names import DB, HTTP

class User(UserMixin):

    def __init__(self, user_doc):
        self.id = str(user_doc.get("_id"))
        self.username = user_doc.get("username")
        self.password = user_doc.get("password") 

        if user_doc.get("spotify", None) and user_doc["spotify"] != {}:
            self.tokens = {
                "access": user_doc["spotify"]["tokens"].get("access"),
                "refresh": user_doc["spotify"]["tokens"].get("refresh")
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
    def access_token(self) -> str:
        """Returns the spotify API access token that belongs to the user.

        :return: The access token belonging to the user, if it exists.
        :rtype: string
        """
        # TODO: Perhaps can check if it doesnt exist, and start oAuth flow if so???
        # -- Maybe check in mongo before auth flow?

        access_token = self.tokens.get("access")
        return access_token


    @property
    def spotify_display_name(self) -> Optional[str]:
        """Gets the user's spotify profile display name if it exists.

        :return: The user's spotify profile display name or None.
        :rtype: Optional[str]
        """
        
        if self.spotify_profile is None:
            return None

        return self.spotify_profile.get("display_name")
    

    @property
    def spotify_profile_url(self) -> Optional[str]:
        """Gets the URL that opens the user's profile in Spotify if it exists.

        :return: The url for the user's profile in spotify, or None
        :rtype: Optional[str]
        """
        
        if self.spotify_profile is None:
            return None

        return self.spotify_profile["external_urls"].get("spotify")


    @property
    def spotify_follower_count(self) -> Optional[int]:
        """Gets the total follower count of the user's Spotify profile,
        if it exists.

        :return: The total follower count of user's Spotify profile, if exists.
        :rtype: Optional[int]
        """

        if self.spotify_profile is None:
            return None
        
        return self.spotify_profile["followers"].get("total")

    
    def update_spotify_tokens(self, user_auth_tokens: dict) -> bool:
        """Updates the mongo user doc as well as the User instance with the provided
        Spotify API tokens.

        Only 'access' and 'refresh' tokens are updated on the User instance, while all
        provided values will be updated within the mongo user doc.

        :param user_auth_tokens: Tokens received from Spotify's token route, whether on
        initial exchange or during token refresh. May contain the access token, the 
        refresh token, as well as scope. 
        :type user_auth_tokens: dict
        :return: Whether updating tokens was successful.
        :rtype: bool
        """

        tokens_to_update = {f"spotify.tokens.{key}": value for key, value in user_auth_tokens.items()}
        try: 
            # TODO: Mongo Single Instance
            mongo = MongoClient(host=DB.MONGO_URI)
            users_collection = mongo[DB.DB][DB.USERS_COLLECTION]

            result = users_collection.update_one(
                {"_id": ObjectId(self.id)}, 
                {"$set": tokens_to_update}
            )
            mongo.close()

            # TODO: Logging, and error handling for the 'Falses'
            if result.matched_count == 1:
                if result.modified_count == 1:
                    print(f"User.update_spotify_tokens() --- User({self.id}) --- Spotify API tokens updated.")

                    if self.tokens is None:
                        self.tokens = {
                            "access": user_auth_tokens.get("access"),
                            "refresh": user_auth_tokens.get("refresh")
                        }
                    else:
                        self.tokens.update(user_auth_tokens)
                        
                    return True
                else:
                    print(f"User.update_spotify_tokens() --- Spotify Tokens for _id {self.id} were not updated")
                    return False
            else:
                print(f"User.update_spotify_tokens() --- No document matched for _id: {self.id}")
                return False

        # TODO: What to do if mongo operation has exception
        except Exception as error:
            print("The error:", error)
            return False

    
    def refresh_access_token(self) -> bool:
        """Refreshes Spotify API access token belonging to the user and updates the users'
        mongo doc along with the instances value. Sometimes the refresh token will also be
        updated along with the access token, this just depend on Spotify's internal API logic.

        :return: Whether or not the refresh was done successfully.
        :rtype: bool
        """

        try:
            new_tokens = SpotifyAuth.refresh_tokens(self.tokens.get("refresh"))
        except Exception as e:
            # TODO
            print(f"User.refresh_access_token() --- Error refreshing token. --- {e}")

        if not new_tokens: # Some issue with refreshing
            return False

        try:
            updated = self.update_spotify_tokens(new_tokens)
            if not updated:
                return False
            
            return True
        except Exception as e:
            # TODO
            print(f"User.refresh_access_token() --- Error when populating user token in mongo. --- {e}")
            return False


    def populate_spotify_profile(self, profile_data: dict) -> bool:
        """Populates the user's mongo document with the given profile data as well as sets the
        current User instances 'spotify_profile' var.

        :param profile_data: The users spotify profile data as returned by the Spotify API /me
        endpoint.
        :type profile_data: dict
        :raises ValueError: If the profile_data parameter is empty or is not a dict throws an error.
        :return: Whether or not the user's profile data was succesfully populated in Mongo.
        :rtype: bool
        """

        if profile_data is None or type(profile_data) != dict:
            raise ValueError("Need to provide an non-empty dictionary with profile data")
        
        try:    
            # TODO: Single Mongo Instance
            mongo = MongoClient(host=DB.MONGO_URI)
            users_collection = mongo[DB.DB][DB.USERS_COLLECTION]

            update_result = users_collection.update_one(
                {"_id": ObjectId(self.id)}, 
                {"$set": {"spotify.profile": profile_data}}
            )
            mongo.close()
        except Exception as e:
            # TODO
            print(f"User.populate_spotify_profile() --- User({self.id}) --- Encountered Mongo Error --- {e}")
            return False

        if update_result.matched_count == 1:
            if update_result.modified_count == 1:
                print(f"User.populate_spotify_profile() --- User({self.id}) --- Users' Spotify profile was updated successfully")
                
                # At the moment, this function is to be used during user creation, so don't need to check if dict.update() is to be used
                self.spotify_profile = profile_data
                return True
            else:
                print(f"User.populate_spotify_profile() --- User({self.id}) --- User's spotify profile was not updated...")
                return False
        else:
            print(f"User.populate_spotify_profile() --- User({self.id}) --- Could not find the user doc to update profile.")
            return False


    def get_spotify_profile_img(self) -> Optional[str]:
        """Get's the valid Spotify profile image url if it exists. Image url's expire after some time, 
        so this function ensures that the most recent URL is returned. 

        :return: The url for the most recent Spotify profile image if it exists, otherwise None.
        :rtype: Optional[str]
        """

        if self.spotify_profile is None:
            return None
        
        images = self.spotify_profile.get("images")
        if images: 
            # Grab the first image as it is the biggest size
            profile_image_url = images[0].get("url")     
            if self._valid_profile_image(profile_image_url):
                return profile_image_url
        else:
            print(f"User.get_spotify_profile_img() --- User({self.id}) --- User's Spotify profile image was not populated.")

        spotify_api = SpotifyAPI(self)
        images = spotify_api.get_profile_images()
        if images:
            # Spotify Profile has images, so need to update
            updated = self._update_profile_images(images)
            if updated:
                profile_image_url = images[0].get("url") 
                return profile_image_url
        else:
            print(f"User.get_spotify_profile_img() --- User({self.id}) --- User does not have an image set for their Spotify profile.")
        
        return None
    

    def get_user_owned_playlists(self) -> list[dict]:
        """Returns a list of playlist objects. First fetches all the playlists associated
        with the user, and then filters out those that are not owned by the user. This returns
        the data that is used in the dashboard view.

        Playlist object: {
            "name": str,
            "snapshot_id": str,
            "id": str,
            "image": str | None,
            "public": bool,
            "collaborative": bool,
            "tracks": {"total": int}
        }

        :return: A list of playlist objects owned by the user, if user owns none, an empty list is returned
        :rtype: list[dict]
        """

        # NOTE: If get_user_playlists throws an error in the future, could catch it to have better logging
        # and reasoning for returning empty or partial list
        spotify_api = SpotifyAPI(self)

        playlist_fields = "id, snapshot_id, name, images, owner, public, collaborative, tracks.total"
        all_playlists = spotify_api.get_user_playlists(playlist_fields=playlist_fields)

        if all_playlists:
            
            owned = []
            user_spotify_id = self.spotify_profile.get("id")
            for playlist in all_playlists:

                # Verify that user owns playlist
                owner_id = playlist["owner"].get("id")
                if owner_id != user_spotify_id:
                    print(f"User does not own:", playlist.get("name"))
                    continue
                
                # Get the largest playlist image, if it exists
                playlist_image = playlist.get("images", [])
                playlist_image = playlist_image[0].get("url") if playlist_image else None
                
                # Edit playlist object
                del playlist["images"]
                del playlist["owner"]
                playlist["image"] = playlist_image

                owned.append(playlist)

            print(f"User.get_user_owned_playlists --- User({self.id}) --- User owns {len(owned)} playlists.")
            return owned

        print(f"User.get_user_owned_playlists --- User({self.id}) --- Either no playlist associated with user account, or error encountered.")
        return []


    def _update_profile_images(self, images: list) -> bool:
        """Updates the user's profile images within the Mongo User doc and the User instance.
        This function assumes that the 'images' provided is a non-empty list, therefore not
        sanity checks.

        :param images: The images list provided by the Spotify API
        :type images: list
        :return: Whether or not the images were successfully updated
        :rtype: bool
        """
        
        # Update Mongo
        try: 
            # TODO: Single Mongo Instance
            mongo = MongoClient(host=DB.MONGO_URI)
            users_collection = mongo[DB.DB][DB.USERS_COLLECTION]

            result = users_collection.update_one(
                {"_id": ObjectId(self.id)}, 
                {"$set": {"spotify.profile.images": images}}
            )
            mongo.close()
        except Exception as e:
            print(f"User._update_profile_images() --- User({self.id}) --- Encountered mongo error, images were not updated. --- {e}")
            return False

        if result.matched_count == 1:
            if result.modified_count == 1:
                print(f"User._update_profile_images() --- User({self.id}) --- Spotify profile images were updated.")
                self.spotify_profile["images"] = images
                return True
            else:
                print(f"User._update_profile_images() --- User({self.id}) --- Did not update Spotify profile images.")
                return False
        else:
            print(f"User._update_profile_images() --- User({self.id}) --- Couldn't find user Mongo Doc to update spotify profile images.")
            return False

    
    def _valid_profile_image(self, img_url: str) -> bool:
        """Checks if the provided spotify profile image url is valid, meaning returns a 200
        status code so that it can be displayed client side. This function assumes, that 
        'img_url' is provided and is a string, so no error checking.

        :param img_url: URL provided by Spotify API for the users profile image, that we 
        are checking validity for.
        :type img_url: str
        :return: Whether or not the url is valid (200) or not (!= 200, most likely 4xx)
        :rtype: bool
        """
        
        try:
            response = requests.get(img_url)
        except Exception as e:
            # TODO
            print(f"User._is_profile_image_valid() --- User({self.id}) --- There was an error checking url validity. --- {e}")
            return False

        if response.status_code != HTTP.OK:
            # TODO: Log
            print(f"User._is_profile_image_valid() --- User({self.id}) --- Profile image url expired!")
            return False
        
        return True
