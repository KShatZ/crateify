import { useContext } from "react";
import { useLoaderData } from "react-router-dom";

import Navbar from "../components/nav/Navbar";
import MetaCarousel from "../components/meta-carousel/MetaCarousel";
import SpotifyProfileImg from "../components/meta-carousel/items/SpotifyProfileImg";
import SpotifyProfileMeta from "../components/meta-carousel/items/SpotifyProfileMeta";
import PlaylistHeader from "../components/headers/playlist-header/PlaylistHeader";
import Playlists from "../components/playlists/Playlists";
import { CurrentUser } from "../field_names";


export default function Dashboard() {

    const currentUser = useContext(CurrentUser);
    const userPlaylists = useLoaderData();

    const spotifyDisplayName = currentUser.spotify_profile.display_name;
    const spotifyProfileImg = currentUser.spotify_profile.profile_image;

    const carouselItems = [
        <SpotifyProfileImg key="spotify-profile-image" img={spotifyProfileImg}/>,
        <SpotifyProfileMeta key="spotify-profile-meta" />,
    ]

    return (
        <>
            <Navbar />
            <MetaCarousel items={carouselItems} />
            <div style={{textAlign: "center"}} className="container">
                <h1 id="meta-title">{spotifyDisplayName}</h1>
            </div>
            <PlaylistHeader />
            <Playlists playlists={userPlaylists} />
        </>
    )

}