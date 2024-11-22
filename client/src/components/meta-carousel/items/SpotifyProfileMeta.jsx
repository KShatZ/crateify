
export default function SpotifyProfileMeta({ spotifyProfile, onTouchStart, onTouchMove, onTouchEnd }) {

    const profileURL = spotifyProfile.url;
    const followerCount = spotifyProfile.follower_count;
    const followingCount = spotifyProfile.following_count;

    return (

        <div 
            id="profile-meta-container" 
            className="carousel-item-container grey-border-2"
            onTouchStart={onTouchStart}
            onTouchMove={onTouchMove}
            onTouchEnd={onTouchEnd} 
        >
            <ul>
                <li>Followers: {followerCount}</li>
                <li>Following: {followingCount}</li>
            </ul>

            <a 
                id="carousel-spot-profile-url" 
                className="grey-border-2" 
                href={profileURL} 
                target="_blank" 
                rel="noreferrer"
            >    
                Open Spotify Profile
            </a>
        </div>
    );
}
