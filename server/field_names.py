from os import getenv
from urllib.parse import urlencode

class DB:

    MONGO_URI = getenv("MONGO_URI", "localhost")

class HTTP:    
    # ------ Status Codes ------ #
    OK = 200
    CREATED = 201

    SEE_OTHER = 303

    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    CONFLICT = 409
    TOO_MANY = 429

    SERVER_ERROR = 500

class SPOTIFY:
    
    CLIENT_ID = getenv("SPOTIFY_CLIENT_ID")
    CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET")

    TOKEN_ENDPOINT = "https://accounts.spotify.com/api/token"
    AUTH_GRANT = "authorization_code"
    REFRESH_GRANT = "refresh_token"
    
    OAUTH_BASE_URL = "https://accounts.spotify.com/authorize"
    def oauth_url():
        url_params = {
            "client_id": SPOTIFY.CLIENT_ID,
            "redirect_uri": SPOTIFY.REDIRECT_URI,
            "scope": SPOTIFY.SCOPE,
            "response_type": "code",
            "show_dialog": True
        }
        oauth_url = SPOTIFY.OAUTH_BASE_URL + "?" + urlencode(url_params)

        return oauth_url
    
    REDIRECT_URI = getenv("SPOTIFY_REDIRECT_URI")
    SCOPE = getenv("SPOTIFY_SCOPE")

    API_BASE_URL = "https://api.spotify.com/v1"

    PARAM_TRACK_LIMIT = 100

class CAMELOT:

    PITCH_CLASS = {
        "0": "C",
        "1": "Df",
        "2": "D",
        "3": "Ef",
        "4": "E",
        "5": "F",
        "6": "Fs",
        "7": "G",
        "8": "Af",
        "9": "A",
        "10": "Bf",
        "11": "B"
    }

    MAJOR = {
        "E": "12B",
        "B": "1B",
        "Fs": "2B",
        "Df": "3B",
        "Af": "4B",
        "Ef": "5B",
        "Bf": "6B",
        "F": "7B",
        "C": "8B",
        "G": "9B",
        "D": "10B",
        "A": "11B",
    }
    
    MINOR = {
        "Df": "12A",
        "Af": "1A",
        "Ef": "2A",
        "Bf": "3A",
        "F": "4A",
        "C": "5A",
        "G": "6A",
        "D": "7A",
        "A": "8A",
        "E": "9A",
        "B": "10A",
        "Fs": "11A",
    }
