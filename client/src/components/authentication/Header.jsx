import spotifyLogo from "../../assets/spotify_assets/icon/Spotify_Icon_RGB_Green.png"
import "./styles.css";

export default function Header() {
        
    // Logo and Name will be changed in the future, just need to come up with it.
    return (
        <div id="auth-header-container" className="accent container">
            <img id="auth-app-logo" src={ spotifyLogo } alt="" />
            <h1 >Spotify Visualizer</h1>
            <hr/>
        </div>
    )
}