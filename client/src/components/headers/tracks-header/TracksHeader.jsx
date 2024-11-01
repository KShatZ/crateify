import FilterToggleSVG from "../FilterToggleSVG";

import "../styles.css";

export default function TracksHeader() {

    return (
        <div className="header-container bg-color elevated container">

            <div className="header-title-container">
                <h2>Tracks:</h2>
                <div id="tracks-audio-features">
                    <p className="pointer">BPM</p>
                    <p className="pointer">KEY</p>
                </div>
            </div>
            <hr/>
            {/* Todo: Filter Component */}
            <FilterToggleSVG />

        </div>
    )

}