import { HTTP } from "../../field_names";

export default async function playlistLoader(params, request) {
    
    let endpoint = `/api/playlist/${params.playlistID}`;
    const snapID = new URL(request.url).searchParams.get("snap_id");

    if (snapID) {
        endpoint = endpoint + "?snap_id=" + encodeURIComponent(snapID);
    }

    try {
        const response = await fetch(endpoint, {
            method: "get",
            credentials: "include",
        });
    
        const status = response.status;
        switch (status) {

            case HTTP.OK: {        
                const responseBody = await response.json();
                const playlist = {
                    meta: responseBody.data.meta,
                    tracks: responseBody.data.tracks,
                }

                return playlist;        
            }

            case HTTP.SERVER_ERROR:
                // TODO: What to do on server error
                return {
                    meta: {},
                    tracks: []
                }
            
            default:
                // TODO
                throw("Hit default playlistLoader case, got an unexpected status")
        }
        

    } catch(error) {
        // TODO: Better error handling, look into react-router useRouteError()
        throw "There was an error fetching playinst data", error;
    }
}