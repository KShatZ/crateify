import { useLoaderData } from "react-router-dom";

import Navbar from "../components/nav/Navbar";
import MetaCarousel from "../components/meta-carousel/MetaCarousel";
import SpotifyPlaylistImg from "../components/meta-carousel/items/SpotifyPlaylistImg";
import TracksHeader from "../components/headers/tracks-header/TracksHeader";
import Tracks from "../components/tracks/Tracks";

import spotifyLogo from "../assets/spotify_assets/icon/Spotify_Icon_RGB_Green.png";

export default function Playlist() {

    const playlist = useLoaderData();

    console.log(playlist)

    const carouselItems = [
        <SpotifyPlaylistImg key="spotify-playlist-img" img={playlist.meta.cover_art} />,
    ];

    return (
        <>
            <Navbar />
            <MetaCarousel items={carouselItems} />
            <div style={{textAlign: "center"}} className="container">
                <h1 id="meta-title">{playlist.meta.name}</h1>
                <p id="playlist-duration">{playlist.duration}</p> 
            </div>
            <TracksHeader />
            <div className="container">
                <p id="playlist-track-count">Total: {playlist.meta.total_tracks}</p>
            </div>
            <Tracks tracks={playlist.tracks}/>
        </>
    )

}