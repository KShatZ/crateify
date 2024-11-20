from flask import request
from flask_login import login_required, current_user

from ...helpers.spotify.spotify_api import SpotifyAPI
from ...helpers.response import create_response

from . import Dashboard as bp


@bp.get("/dashboard")
@login_required
def get_dashboard_data():

    # Data thats needed:
    #   - Spotify Profile Info
    #       Profile Name, Profile Img, Profile Link, Follower/Following Count
    #   - Playlists
    
    spotify_api = SpotifyAPI(current_user)

    spotify_profile = {
        "url": current_user.spotify_profile_url,
        "display_name": current_user.spotify_display_name,
        "follower_count": current_user.spotify_follower_count,
        "following_count": spotify_api.get_following_count(),
        "image": current_user.get_spotify_profile_img()
    }

    # TODO: Playlist stuff

    return create_response(data=spotify_profile)