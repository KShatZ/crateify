import { forwardRef } from "react";
import { Link } from "react-router-dom";

import "./styles.css";


const DropdownMenu = forwardRef(({ isVisible }, ref) => {

    return (
        <div 
            id="navbar-dropdown-container" 
            className="container" 
            style={ isVisible ? { top: "65px" } : {} }
        >
            <ul id="nav-dropdown-menu" ref={ ref }>
                {/* Todo: Links */}
                <li>Account</li> 
                <li><Link to={ "/logout" }>Logout</Link></li>
            </ul>
        </div>
    )

});

DropdownMenu.displayName = "DropdownMenu";
export default DropdownMenu;
