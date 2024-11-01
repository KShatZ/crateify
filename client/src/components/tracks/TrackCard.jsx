import { Link } from "react-router-dom";

import "./styles.css"

export default function TrackCard({ spotifyID, coverArt, name, artists, bpm, camelotKey }) {

    return (
        <Link to="#" id="track" >
            <div className="track-album-cover grey-border-3">
                <img src={coverArt}></img>
            </div>

            <div className="track-meta">
                <h3 className="track-name pointer">{name}</h3>
                <p className="track-artists pointer">{artists}</p>
            </div>

            <div className="track-audio-features">
                <p className="pointer">{bpm}</p>
                <p className="pointer">{camelotKey}</p>
            </div>
        </Link>
    )
}