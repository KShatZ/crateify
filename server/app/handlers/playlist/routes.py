from flask import request
from flask_login import login_required, current_user

from . import Playlist as bp
from ...models.playlist import Playlist


@bp.get("/playlist/<playlist_id>")
@login_required
def fetch_playlist(playlist_id):

    # NOTE: Perhaps some playlist_id check??

    # If user hits this endpoint from dashboard, always guranteed to have most
    # recent snap_id.
    snap_id = request.args.get("snap_id")

    playlist = Playlist(playlist_id, current_user, snap_id=snap_id)
    # TODO: Populate Playlist with data



    # In response, should signify if playlist was pulled from spotify and 
    # cached with most recent snap_id, so that the client can change the URL to the most recent
    # snap_id in order to precent new fetches on refresh.