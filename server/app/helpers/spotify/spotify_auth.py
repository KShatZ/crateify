import requests
import base64
from urllib.parse import urlencode

from field_names import SPOTIFY, HTTP


class SpotifyAuth():

    @classmethod
    def auth_headers(cls):
        return {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {cls.base64_auth_string()}",
        }

    @staticmethod
    def spotify_oauth_url():
        """Generates the url that takes user to the Spotify oAuth splash page
        in order to give app access to their Spotify data.

        :return: URL containing proper query params for linking user confirmation
        with the app.
        :rtype: string
        """

        url_params = {
            "client_id": SPOTIFY.CLIENT_ID,
            "redirect_uri": SPOTIFY.REDIRECT_URI,
            "scope": SPOTIFY.SCOPE,
            "response_type": "code",
            "show_dialog": True
        }
        oauth_url = SPOTIFY.OAUTH_BASE_URL + "?" + urlencode(url_params)

        return oauth_url
    

    @staticmethod
    def base64_auth_string():
        """Generates a base64 encoded string to be used in the Authorization header
        when exchanging code for user access/refresh tokens.

        :return: base64 encoded auth string
        :rtype: string
        """
        auth_string = f"{SPOTIFY.CLIENT_ID}:{SPOTIFY.CLIENT_SECRET}".encode("utf-8")
        return base64.b64encode(auth_string).decode("utf-8")
    
    
    @staticmethod
    def request_auth_tokens(code):
        """Exchanges auth code which is given when user grants app permission from Spotify
        oAuth page, for access and refresh tokens to be used for making API calls on the users
        behalf.

        :param code: Authorization code given by Spotify oAuth, to be exchanged for API tokens.
        :type code: string
        :return: Access and refresh tokens as well as the api scope permissions associated with
        the access tokens.
        :rtype: dict
        """

        endpoint = SPOTIFY.TOKEN_ENDPOINT
        headers = SpotifyAuth.auth_headers()
        params = {
            "grant_type": SPOTIFY.GRANT_TYPE_EXCHANGE_CODE,
            "code": code,
            "redirect_uri": SPOTIFY.REDIRECT_URI
        }

        try: 
            response = requests.post(endpoint, headers=headers, params=params)

            # TODO - Decide what to do if not succesfully exchanged...
            # Try again a couple times and eventually return None?
            if response.status_code != HTTP.OK:
                return None # Temporary
        
            response_data = response.json() # NOTE: This can throw, maybe seperate try for it?

            access_token = response_data.get("access_token")
            refresh_token = response_data.get("refresh_token")
            scope = response_data.get("scope")

            # TODO - What to do if response doesnt contain data?
            # Request again (this might not be possibile), raise exception, etc...
            if not access_token or not refresh_token or not scope:
                return None # Temporary

            tokens = {
                "access": access_token,
                "refresh": refresh_token,
                "scope": scope,
            }
            return tokens

        # TODO - What to do on request fail
        except Exception as ExchangeError:
            print(f"SpotifyAuth.request_auth_token() --- There was an error exchaning tokens... --- {ExchangeError}")
            return None #Temporary
        

    @staticmethod
    def refresh_tokens(refresh_token):

        if not refresh_token:
            # TODO: Log
            print("SpotifyAuth.refresh_tokens() --- Can't refresh... 'refresh_token' was not provided")
            raise ValueError("Provide a value for refresh_token.") 

        endpoint = SPOTIFY.TOKEN_ENDPOINT
        headers = SpotifyAuth.auth_headers()
        params = {
            "grant_type": SPOTIFY.GRANT_TYPE_REFRESH_CODE,
            "refresh_token": refresh_token
        }

        try:
            response = requests.post(endpoint, headers=headers, params=params)
            status = response.status_code

            if status != HTTP.OK:
                # TODO: What to do when refresh doesnt work -- retry a couple times??
                print(f"SpotifyAuth.refresh_tokens() --- Failed to refresh access token.")
                return None

            response_data = response.json() # NOTE: This can throw

            access_token = response_data.get("access_token")
            refresh_token = response_data.get("refresh_token")

            if not access_token:
                # TODO: What to do if access_token not present -- Try again, if refresh is still gucci?
                print(f"SpotifyAuth.refresh_tokens() --- Refresh request was succesful, but did not receive access token...")
                return None
            
            tokens = {"access": access_token}
            if refresh_token: # Sometimes a new refresh token is provided
                tokens["refresh"] = refresh_token

            return tokens
        except Exception as RefreshError:
            # TODO: What to do on error
            print(f"SpotifyAuth.refresh_token() --- Error when refreshing tokens... --- {RefreshError}")
