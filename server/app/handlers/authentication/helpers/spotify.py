import requests

from field_names import SPOTIFY


def obtain_tokens(code):
    """Swaps the code received during user authorization step in
    Spotify auth flow for the access and refresh token. Send a post 
    request to the Spotify access token endpoint

    :param code: Code received during user authorization step
    :type code: str
    :raises Exception: Any error encountered during fetch to 
    Spotify endpoint
    :return: The access token, refresh token, and access scope.
    :rtype: dict
    """

    endpoint = SPOTIFY.TOKEN_ENDPOINT
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    params = {
        "client_id": SPOTIFY.CLIENT_ID,
        "client_secret": SPOTIFY.CLIENT_SECRET,
        "redirect_uri": SPOTIFY.REDIRECT_URI,
        "grant_type": "authorization_code",
        "code": code
    }

    try:
        r = requests.post(endpoint, headers=headers, params=params)
        data = r.json()
    except Exception as SpotifyError:
        # - Log - #
        print("acquire_access_token -- Error during request to obtain access token")
        raise SpotifyError("acquire_access_token -- Error during request to obtain access token")

    return {
        "access_token": data.get("access_token"),
        "refresh_token": data.get("refresh_token"),
        "scope": data.get("scope")
    }


def get_user_spotify_profile(access_token):
    """Sends a request to the Spotify API '/me' endpoint, which returns data on the
    current user's Spotify profile.

    :param access_token: The users' Spotify access Token
    :type access_token: str
    :raises SpotifyError: Error during request to Spotify
    :return: The spotify profile data pertaining to the current user
    :rtype: dict
    """

    url = SPOTIFY.API_BASE_URL + "/me"
    headers = {"Authorization": "Bearer " + access_token}

    try:
        r = requests.get(url, headers=headers)

        data = r.json()
        data.pop("uri")
        data.pop("explicit_content")

        return data

    except Exception as SpotifyError: #TODO
        # - Log - #
        print("get_user_spotify_profile -- Error during request to get users profile data")
        raise SpotifyError("get_user_spotify_profile -- Error during request to get users profile data")
    
