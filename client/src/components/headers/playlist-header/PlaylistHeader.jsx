import SortView from "../SortView";
import FilterToggleSVG from "../FilterToggleSVG";

import "../styles.css";

export default function PlaylistHeader() {

    return (
        <div className="header-container bg-color elevated container">

            <div className="header-title-container">
                <h2>Your Playlists:</h2>
                <SortView type={ "default" } column={undefined}/>
            </div>
            <hr/>
            {/* Todo: Filter Component */}
            <FilterToggleSVG />

        </div>
    )

}
