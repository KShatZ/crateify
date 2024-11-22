import { useLoaderData } from "react-router-dom";

import Navbar from "../components/nav/Navbar";
import MetaCarousel from "../components/meta-carousel/MetaCarousel";
import SpotifyProfileImg from "../components/meta-carousel/items/SpotifyProfileImg";
import SpotifyProfileMeta from "../components/meta-carousel/items/SpotifyProfileMeta";
import PlaylistHeader from "../components/headers/playlist-header/PlaylistHeader";
import Playlists from "../components/playlists/Playlists";


export default function Dashboard() {

    const loaderData = useLoaderData();
    const spotifyProfile = loaderData.spotify_profile;
    const playlists = loaderData.playlists;

    const carouselItems = [
        <SpotifyProfileImg key="spotify-profile-image" img={spotifyProfile.image} />,
        <SpotifyProfileMeta key="spotify-profile-meta" spotifyProfile={spotifyProfile} />,
    ]

    return (
        <>
            <Navbar />
            <MetaCarousel items={carouselItems} />
            <div style={{textAlign: "center"}} className="container">
                <h1 id="meta-title">{spotifyProfile.display_name}</h1>
            </div>
            <PlaylistHeader />
            <Playlists playlists={playlists.playlists} />
        </>
    )
}