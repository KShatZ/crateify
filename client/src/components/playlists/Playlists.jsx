import PlaylistCard from "./PlaylistCard";

import spotifyLogo from "../../assets/spotify_assets/icon/Spotify_Icon_RGB_Green.png"
import "./styles.css";


export default function Playlists({ playlists }) {
    return (
        <div id="playlists-container" className="container">
            {
                playlists.map((playlist) => {
                    
                    if (!playlist.image) {
                        playlist.image = spotifyLogo;
                    }

                    return (
                        <PlaylistCard 
                            key={playlist.id}
                            spotifyID={playlist.id}
                            playlistName={playlist.name}
                            playlistImage={playlist.image}
                            trackCount={playlist.track_count}
                            isPublic={playlist.public}
                            snapID={playlist.snapshot_id}
                        />
                    )
                })
            }
        </div>
    )
}
