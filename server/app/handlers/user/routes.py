from flask import request
from flask_login import current_user, login_required

from . import User as bp
from ...models import Playlist
from ...helpers.spotify_api import SpotifyAPI
from ...helpers.response import create_response


@bp.get("/user/playlists")
@login_required
def get_user_playlists():
    #TODO: Error Handling?? 

    user_playlists = current_user.get_spotify_playlists()
    
    data = {"playlists": user_playlists}
    return create_response(data=data)


@bp.get("/user/playlist/<playlist_id>")
@login_required
def get_user_playlist(playlist_id):

    snap_id = request.args.get("snap_id")

    playlist = Playlist(user_id=current_user.id, playlist_id=playlist_id, snap_id=snap_id)

    if playlist.meta:
        body = {
            "meta": playlist.meta,
            "duration": playlist.duration,
            "tracks": [track.serialize() for track in playlist.tracks],
        }

        return create_response(data=body)

    return create_response()
