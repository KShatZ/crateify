import time

import requests

from ...models.user import User
from field_names import SPOTIFY, HTTP


class SpotifyAPI():

    SUCCESS_CODES = [HTTP.OK, HTTP.CREATED]
    MAX_RETRY = 5

    def __init__(self, user: User):
        self.user = user


    @property
    def auth_header(self) -> dict:
        """Return an "Authorization" header with the current value of access token on 
        the user object.

        :return: Header dictionary to be used in API request
        :rtype: dict
        """

        header = {
            "Authorization": f"Bearer {self.user.access_token}"
        }
        return header


    def send_request(self, method: str = "get", endpoint: str = None, url: str = None, params: dict = None):

        if endpoint is None and url is None:
            # TODO: What to do when neither are provided
            print("SpotifyAPI.send_request() --- Can't send request to spotify api, need to have an endpoint or url provided.")
            raise ValueError("Need to provide either an 'endpoint' or 'url' value to send request too.")
        
        spotify_api_url = None
        if endpoint:
            if not endpoint.startswith("/"): # This honestly might not even be needed, more for the dev
                print(f"SpotifyAPI.send_request() --- Cant send request. Endpoint needs to start with '/' but got {endpoint}.")
                raise ValueError(f"Endpoint needs to start with '/' but got {endpoint}")
            
            spotify_api_url = SPOTIFY.API_BASE_URL + endpoint
        else:
            # TODO: Sanity checks on URL?? -- Might not even be needed, more for dev
            spotify_api_url = url
        
        response = {"status_code": None, "data": None}
        request_count = 1
        while(request_count <= SpotifyAPI.MAX_RETRY):

            try:
                # TODO: Log
                print(f"SpotifyAPI.send_request() --- User({self.user.id}) --- {method.upper()}:{spotify_api_url} --- [Attempt {request_count}] Sending...")
                request = requests.request(method=method, url=spotify_api_url, headers=self.auth_header, params=params)
            except Exception as e:
                # TODO
                r = {"method": method, "url": spotify_api_url, "headers": self.auth_header, "params": params}
                print(f"SpotifyAPI.send_request() --- Error sending request: {r} --- {e}")

            status = request.status_code
            
            # NOTE: Consider using a dict dispatch for the codes instead of if.
            # --- 2XX Codes --- #
            if status in SpotifyAPI.SUCCESS_CODES:
                # NOTE: Consider including retry history in response object
                # TODO: Try/Except - For json() in case its not valid
                
                print(f"SpotifyAPI.send_request() --- User({self.user.id}) --- [{status}]:{method.upper()}:{spotify_api_url} --- Request successful.")

                response["status_code"] = status
                response["data"] = request.json()
                return response

            # --- 4XX Codes --- #
            if status == HTTP.UNAUTHORIZED: # Access Token Expired
                try:
                    print(f"SpotifyAPI.send_request() --- User({self.user.id}) --- [{status}]:{method.upper()}:{spotify_api_url} --- Access Token expired, refreshing.") # TODO: Log
                    refreshed = self.user.refresh_access_token()

                    if not refreshed:
                        # TODO: Come back to this. - Logging - Back off - Other func
                
                        # Try to refresh 3 more times
                        refresh_count = 1
                        while not refreshed or refresh_count <= 3:
                            print(f"SpotifyAPI.send_request() --- User({self.user.id}) --- [{status}]:{method.upper()}:{spotify_api_url} --- Retrying token refresh, attempt {refresh_count}")
                            refreshed = self.user.refresh_access_token()
                            refresh_count +=1
                        
                        if not refreshed:
                            print(f"SpotifyAPI.send_request() --- User({self.user.id}) --- [{status}]:{method.upper()}:{spotify_api_url} --- Request not complete, failed to refresh token.")
                            response["status_code"] = status
                            response["data"] = request.json()

                    request_count += 1
                    continue
                except Exception as e:
                    # TODO
                    print(f"SpotifyAPI.send_request() --- User({self.user.id}) --- [{status}]:{method.upper()}:{spotify_api_url} --- Request not complete, error during token refresh --- {e}")
                    continue


            if status == HTTP.FORBIDDEN:
                # TODO
                # Not sure when would get this, could be valid auth, but using for wrong user??
                print(f"SpotifyAPI.send_request() --- User({self.user.id}) --- [{status}]:{method.upper()}:{spotify_api_url} --- Request not complete, was forbidden, idk m8")
                response["status_code"] = status
                response["data"] = request.json()
                return response

            
            if status == HTTP.TOO_MANY: # Rate Limit on API
                # TODO: Better back off strategy, request might contain a "Retry After" Header

                print(f"SpotifyAPI.send_request() --- User({self.user.id}) --- [{status}]:{method.upper()}:{spotify_api_url} --- Too many API requests, backing off for 10 seconds")
                time.sleep(10) # This is a dummy value, this functionality is not yet done
                request_count += 1
                continue

            # --- 5XX Codes --- #
            if status == HTTP.SERVER_ERROR:
                
                print(f"SpotifyAPI.send_request() --- User({self.user.id}) --- [{status}]:{method.upper()}:{spotify_api_url} --- Server error, backing off and trying again.")

                if request_count > 1:
                    back_off = .25 * request_count
                    time.sleep(back_off)

                request_count += 1
                continue

        # After 5 retries, still a unsuccessful request

        print(f"SpotifyAPI.send_request() --- User({self.user.id}) --- [{status}]:{method.upper()}:{spotify_api_url} --- Reached max retry.")
        response["status_code"] = status
        response["data"] = request.json() # Most likely an error object if it exists
        return response
