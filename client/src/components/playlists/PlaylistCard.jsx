import { Link } from "react-router-dom";

export default function PlaylistCard({ spotifyID, playlistName, playlistImage, trackCount, isPublic, snapID }) {

    const href = `/playlist/${spotifyID}?snap_id=` + encodeURIComponent(snapID);

    return (
        <Link to={href} className="playlist-card" >
            <div className="playlist-card-album-art grey-border-3">
                <img src={playlistImage}></img>
            </div>

            <div className="playlist-card-meta">
                <h3 className="playlist-name pointer">{playlistName}</h3>
                <p className="playlist-track-count pointer">Tracks: {trackCount}</p>
            </div>

            <div className="playlist-card-arrow">
                <svg width="20px" height="20px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <g id="SVGRepo_bgCarrier" strokeWidth="0"/>
                    <g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"/>
                    <g id="SVGRepo_iconCarrier"> <path fillRule="evenodd" clipRule="evenodd" d="M15.7071 4.29289C16.0976 4.68342 16.0976 5.31658 15.7071 5.70711L9.41421 12L15.7071 18.2929C16.0976 18.6834 16.0976 19.3166 15.7071 19.7071C15.3166 20.0976 14.6834 20.0976 14.2929 19.7071L7.29289 12.7071C7.10536 12.5196 7 12.2652 7 12C7 11.7348 7.10536 11.4804 7.29289 11.2929L14.2929 4.29289C14.6834 3.90237 15.3166 3.90237 15.7071 4.29289Z" fill="rgba(250, 249, 246, .4)" /> </g>
                </svg>
            </div>
        </Link>
    )
}
