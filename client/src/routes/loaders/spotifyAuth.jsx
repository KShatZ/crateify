import { redirect } from "react-router-dom";

/**
 * After a user grants or declines access to their Spotify data, 
 * Spotify will redirect them to the clients /auth/spotify/tokens 
 * route which is essentially just this loader that takes the spotify code 
 * or lack thereof and forwards the auth flow along to the server.
 */

export default async function spotifyAuthLoader({ request }) {

    const url = new URL(request.url);
    const searchParams = url.searchParams;

    // Spotify did not send code needed to acquire access token
    if (!searchParams.has("code")) {
        // TODO: Handle 
        return redirect("/login");
    } 

    // TODO: Try/Catch
    const r = await fetch("/api/auth/spotify/tokens", {
        method: "post",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({code: searchParams.get("code")}),
        credentials: "include"
    });

    const status = r.status;

    /**
     *  TODO: Handle Flow for 400 and 500 responses.
     */
    if (status == 200) {
        return redirect("/");
    } else {
        return redirect("/login");
    }
}