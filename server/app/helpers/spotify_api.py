import requests
import time

from bson import ObjectId
from pymongo import MongoClient

from field_names import DB, SPOTIFY, HTTP

mongo = MongoClient(host=DB.MONGO_URI)
USERS_COLLECTION = mongo["spotify-visualizer"]["users"]

class SpotifyAPI():

    def __init__(self, user_id, method="get", endpoint="", url="", params=None, headers={}):
    
        self.request_count = 0
        self.user_id = user_id
        self.method = method.lower()       
        self.endpoint = endpoint
        self.url = url
        self.params = params
        self.headers = headers
        self.access_token = self._access_token(user_id)
        
        self.response_data = None # Populated After Succesful Response


    def send(self):
        """Main function of SpotifyAPI class, sends the configured request to the
        Spotify API. Handles refreshing access token if needed.

        This function returns the entire Response object, but also populates the
        `response_data` instance variable with the response data on succesful request.

        :return: The response received from Spotify, or None
        :rtype: python requests Response object
        """

        # Limit requests
        if self.request_count > 4:
            return None

        self.headers["Authorization"] = f"Bearer {self.access_token}"

        url = SPOTIFY.API_BASE_URL + self.endpoint if not self.url else self.url

        # TODO: Try Block
        r = requests.request(self.method, url, params=self.params, headers=self.headers)
        status = r.status_code

        # Access Token Bad - Refresh Token/Try Again
        if status == HTTP.UNAUTHORIZED:
            # - Log - #
            print(f"SpotifyAPI -- Bad Access Token for user_id:{self.user_id} on {self.method.upper} {self.endpoint} - Refreshing...")
             
            # For some reason, token did not refresh
            if not self._refresh_user_access_token(self.user_id):
                # TODO: Handle what to do on refresh failure
                # - Try again 2-3 times
                # - If still fail decide what to do:
                #   It could be an error on our end (don't need to reauth)
                #   But could be something with spotify, so reauthenticate
                pass

            self.request_count += 1
            return self.send()

        # Spotify Issue - Time Out/Try Again
        if status == HTTP.SERVER_ERROR:
            # - Log - #
            print(f"SpotifyAPI -- user:{self.user_id} - 500 for: {self.method} {self.endpoint} - Trying again in 2 seconds")
            time.sleep(2)

            self.request_count += 1
            return self.send()
        
        # oAuth Issue on Our End - TODO
        if status == HTTP.FORBIDDEN:
            # - Log - #
            print(f"SpotifyAPI -- user:{self.user_id} - 403 for: {self.method} {self.endpoint} - The response: {r.json()}")
            return None
        
        # Spotify Rate Limiting - Time Out/Try Again
        if status == HTTP.TOO_MANY:
            # Timeout may need to be way longer than 5, but also prob different implementation
            # in general. Something like a modal popup on user end. But this a TODO

            # - Log - #
            print(f"SpotifyAPI -- user:{self.user_id} - Too many requests on this last request: {self.method} {self.endpoint} - Trying again in 5 seconds")
            time.sleep(5)
            
            self.request_count += 1
            return self.send()

        self.response_data = r.json()
        return r
        

    def _access_token(self, user_id):
        """Returns the spotify access token for the provided user_id.

        :param user_id: The user _id
        :type user_id: str
        :raises MongoError: Error that occured during Mongo query.
        :return: The spotify access token, or None
        :rtype: str
        """

        try:
            user = USERS_COLLECTION.find_one({"_id": ObjectId(user_id)}, {"spotify.access_token": True})
        except Exception as MongoError:
            # - Log - #
            print("access_token -- Mongo Error while getting current users token")
            raise MongoError(f"Mongo Error while getting current users token: {MongoError}")
        
        access_token = user["spotify"].get("access_token", None)

        return access_token
    

    def _refresh_user_access_token(self, user_id):
        """Refreshes the spotify access token for the user provided.

        :param user_id: The _id of the user to refresh access token for
        :type user_id: str
        :raises MongoError: Mongo Error during querying for or updating users tokens
        :raises SpotifyError: Error during request to Spotify to retrieve new access
        token.
        :return: Whether or not the refresh was succesful, meaning access token was
        updated.
        :rtype: bool
        """

        # Retrieve users spotify refresh token
        try:
            user = USERS_COLLECTION.find_one({"_id": ObjectId(user_id)}, {"spotify.refresh_token": True})
        except Exception as MongoError:
            # TODO: Return False Here?
            # - Log - #
            print("access_token -- Mongo Error while getting current users token")
            raise MongoError(f"Mongo Error while getting current users token: {MongoError}")
        
        refresh_token = user["spotify"].get("refresh_token", None)
        if not refresh_token:
            # - Log - #
            print(f"_refresh_token -- User is missing refresh token - user _id: {user_id}")
            return False
        
        # Get new spotify access_token
        endpoint = SPOTIFY.TOKEN_ENDPOINT
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        params = {
            "grant_type": SPOTIFY.REFRESH_GRANT,
            "refresh_token": refresh_token,
            "client_id": SPOTIFY.CLIENT_ID,
            "client_secret": SPOTIFY.CLIENT_SECRET
        }

        try:
            r = requests.post(endpoint, headers=headers, params=params)
            data = r.json()
        except Exception as SpotifyError:
            # TODO: Return False Here?
            # - Log - #
            print("_refresh_token -- Error during request to refresh access token")
            raise SpotifyError("_refresh_token -- Error during request to refresh access token")
        
        access_token = data.get("access_token", None)
        if not access_token:
            # - Log - #
            # This will not happen with proper status code checks
            print(f"_refresh_token -- Spotify did not send back access_token for user - user _id: {user_id}")
            return False
        
        # Update user's access token
        try:
            result = USERS_COLLECTION.update_one({"_id": ObjectId(user_id)}, {"$set": {"spotify.access_token": access_token}})
        except Exception as MongoError:
            # - Log - #
            print(f"_refresh_token -- Mongo Error while trying to update user's access_token -- {MongoError}")
            raise MongoError
        
        # The update query did not update doc
        if result.modified_count == 0:
            return False
        
        self.access_token = access_token
        return True
