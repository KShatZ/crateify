from urllib.parse import urlparse, parse_qsl

from bson import ObjectId
from flask_login import UserMixin

from ..helpers.spotify_api import SpotifyAPI

class User(UserMixin):

    def __init__(self, user_doc):
        self.id = str(user_doc.get("_id"))
        self.username = user_doc.get("username")

        if user_doc.get("spotify", None):
            self.spotify_profile = user_doc["spotify"].get("profile")
        else:
            self.spotify_profile = None


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
