import { HTTP } from "../../field_names";


// Need to get currentUser's playlists before rendering dashboard
export default async function dashboardLoader() {
    try {
        const response = await fetch("/api/dashboard", {
            method: "GET",
            credentials: "include"
        });
        
        const status = response.status;
        switch (status) {

            case HTTP.OK: {
                const responseBody = await response.json();
                return responseBody.data;
            }
                
            case HTTP.SERVER_ERROR:
                // TODO: What to do on server error
                return {
                    spotify_profile: {},
                    playlists: {
                        total: null,
                        playlists: []
                    }
                }

            default:
                // TODO
                throw("Hit default case, got an unexpected status")
        }

    } catch (error) {
        // TODO: Better error handling, look into react-router useRouteError()
        throw "There was an error fetching dashboard data", error;
    }
}