export default async function playlistLoader(params, request) {
    
    let endpoint = `/api/user/playlist/${params.playlistID}`;
    const snapID = new URL(request.url).searchParams.get("snap_id");

    if (snapID) {
        endpoint = endpoint + "?snap_id=" + encodeURIComponent(snapID);
    }
    
    const response = await fetch(endpoint, {
        method: "get",
        credentials: "include",
    });

    const body = await response.json();

    const playlist = {
        meta: body.data.meta,
        duration: body.data.duration,
        tracks: body.data.tracks,
    }

    return playlist;
}