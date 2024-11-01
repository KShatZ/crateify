export default function SpotifyPlaylistImg({ img, onTouchStart, onTouchMove, onTouchEnd }) {
    
    return (
        <div 
            id="meta-img-container" 
            className="carousel-item-container exit-left grey-border-2"
            onTouchStart={onTouchStart}
            onTouchMove={onTouchMove}
            onTouchEnd={onTouchEnd}
        >
            <img src={img} alt="Spotify Playlist Image" />
        </div>
    )

}