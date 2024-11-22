from flask import request
from flask_login import login_required, current_user

from ...helpers.spotify.spotify_api import SpotifyAPI
from ...helpers.response import create_response
from field_names import HTTP

from . import Dashboard as bp


@bp.get("/dashboard")
@login_required
def get_dashboard_data():
    
    spotify_api = SpotifyAPI(current_user)

    try:
        spotify_profile = {
            "url": current_user.spotify_profile_url,
            "display_name": current_user.spotify_display_name,
            "follower_count": current_user.spotify_follower_count,
            "following_count": spotify_api.get_following_count(),
            "image": current_user.get_spotify_profile_img()
        }
        user_playlists = current_user.get_user_owned_playlists()
    except Exception as e:
        # TODO: Better error handling??
        print(f"GET /dashboard --- User({current_user.id}) --- Encountered error while fetching dashboard data --- {e}")
        return create_response(error=True, status_code=HTTP.SERVER_ERROR, msg="There was an error getting user data.")

    data = {
        "spotify_profile": spotify_profile,
        "playlists": {
            "total": len(user_playlists),
            "playlists": user_playlists
        }
    }
    
    return create_response(data=data)
