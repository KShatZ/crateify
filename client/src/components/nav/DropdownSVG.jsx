import "./styles.css";


export default function DropdownSVG({ isOpen }) {

    return (
        <div id="nav-dropdown-carrot" style={ isOpen ? {transform: "rotate(180deg)", opacity: "1"} : {} }>            
            <svg width="64px" height="64px" viewBox="0 0 24.00 24.00" fill="none" xmlns="http://www.w3.org/2000/svg" stroke={ isOpen ? "rgba(30,215,96,1)" : "rgba(250, 249, 246, .85)" }>
                <g id="SVGRepo_bgCarrier" strokeWidth="0"/>
                <g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"/>
                <g id="SVGRepo_iconCarrier"> <path d="M8 10L12 14L16 10" stroke={ isOpen ? "rgba(30,215,96,1)" : "rgba(250, 249, 246, .85)" } strokeWidth="1.44" strokeLinecap="round" strokeLinejoin="round"/></g>
            </svg>
        </div>
    )
}