import DropdownSVG from "./DropdownSVG";
import "./styles.css";

export default function DropdownToggle({ user, onClick, isOpen }) {

    function handleClick(event) {
        event.stopPropagation(); // Prevent interference with document click listener
        onClick();
    }

    return (
        <div id="nav-dropdown-toggle" className="bg-color"  onClick={ handleClick }>
            <span id="username">{ user }</span>
            <DropdownSVG isOpen={ isOpen } /> 
        </div>
    )
}
