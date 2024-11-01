import TrackCard from "./TrackCard";

import tracksData from "./tracks.json";
import "./styles.css"

export default function Tracks({ tracks }) {

    return (

        <div id="tracks-container" className="container">
            {
                tracks.map((track) => {
                    return (
                        <TrackCard 
                            key={track.id} 
                            coverArt={track.cover_art}
                            name={track.name}
                            artists={track.artists}
                            camelotKey={track.key}
                            bpm={Math.floor(track.bpm)}
                            duration={track.duration}
                            explicit={track.explicit}
                            spotify_url={track.spotify_url}
                            added_at={track.added_at}
                        />
                    )
                })
            }
        </div>
    )

}