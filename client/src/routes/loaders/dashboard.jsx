
// Need to get currentUser's playlists before rendering dashboard
export default async function dashboardLoader() {

    const response = await fetch("/api/user/playlists", {
        method: "GET",
        credentials: "include"
    });

    // TODO - Need to implement other status codes server side first
    if (response.status != 200) {
        console.log("Error getting playlists...");
        return [];
    }

    const body = await response.json();

    const playlists = body.data.playlists || [];
    return playlists;
}