from flask import request
from flask_login import login_required, current_user

from . import Playlist as bp
from ...models.playlist import Playlist
from ...helpers.response import create_response
from field_names import HTTP


@bp.get("/playlist/<playlist_id>")
@login_required
def fetch_playlist(playlist_id):

    # NOTE: Perhaps some playlist_id check??
    snap_id = request.args.get("snap_id")
    playlist = Playlist(playlist_id, current_user, snap_id=snap_id)
    loaded = playlist.load_playlist()

    if not loaded:
        # TODO: Better Error Handling
        return create_response(error=True, status_code=HTTP.SERVER_ERROR)

    # Populate response with playlist meta, tracks
    return create_response(data=playlist.serialize())

    # TODO: In response, should signify if playlist was pulled from spotify and 
    # cached with most recent snap_id, so that the client can change the URL to the most recent
    # snap_id in order to precent new fetches on refresh.