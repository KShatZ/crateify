import { useContext } from "react";

import { CurrentUser } from "../../../field_names";


export default function SpotifyProfileMeta({ onTouchStart, onTouchMove, onTouchEnd }) {

    const currentUser = useContext(CurrentUser);
    const spotify_profile_url = currentUser.spotify_profile.profile_url;
    const spotify_follower_count = currentUser.spotify_profile.follower_count;
    const spotify_following_count = currentUser.spotify_profile.following_count;

    return (

        <div 
            id="profile-meta-container" 
            className="carousel-item-container grey-border-2"
            onTouchStart={onTouchStart}
            onTouchMove={onTouchMove}
            onTouchEnd={onTouchEnd} 
        >
            <ul>
                <li>Followers: {spotify_follower_count}</li>
                <li>Following: {spotify_following_count}</li>
            </ul>

            <a id="carousel-spot-profile-url" className="grey-border-2" href={spotify_profile_url} target="_blank" rel="noreferrer">Open Spotify Profile</a>
        </div>

    );

}
