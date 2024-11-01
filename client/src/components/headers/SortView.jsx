const defaultSVG = (
    <svg className="sort-icon-svg" fill="#faf9f6d9" width="100px" height="100px" viewBox="0 0 24.00 24.00" xmlns="http://www.w3.org/2000/svg" stroke="#faf9f6d9" strokeWidth="0.00024000000000000003">
        <g id="SVGRepo_bgCarrier" strokeWidth="0"/>
        <g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"/>
        <g id="SVGRepo_iconCarrier"> <path d="M6.227 11h11.547c.862 0 1.32-1.02.747-1.665L12.748 2.84a.998.998 0 0 0-1.494 0L5.479 9.335C4.906 9.98 5.364 11 6.227 11zm5.026 10.159a.998.998 0 0 0 1.494 0l5.773-6.495c.574-.644.116-1.664-.747-1.664H6.227c-.862 0-1.32 1.02-.747 1.665l5.773 6.494z"/></g>
    </svg>
);

const ascendingSVG = (
    <svg className="sort-icon-svg" fill="#faf9f6d9" width="100px" height="100px" viewBox="-96 0 512 512" xmlns="http://www.w3.org/2000/svg">
        <g id="SVGRepo_bgCarrier" strokeWidth="0"/>
        <g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"/>
        <g id="SVGRepo_iconCarrier"> <path d="M279 224H41c-21.4 0-32.1-25.9-17-41L143 64c9.4-9.4 24.6-9.4 33.9 0l119 119c15.2 15.1 4.5 41-16.9 41z"/></g>
    </svg>
);

const descendingSVG = (
    <svg className="sort-icon-svg" fill="#faf9f6d9" width="100px" height="100px" viewBox="-96 0 512 512" xmlns="http://www.w3.org/2000/svg">
        <g id="SVGRepo_bgCarrier" strokeWidth="0"/>
        <g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"/>
        <g id="SVGRepo_iconCarrier"> <path d="M41 288h238c21.4 0 32.1 25.9 17 41L177 448c-9.4 9.4-24.6 9.4-33.9 0L24 329c-15.1-15.1-4.4-41 17-41z"/></g>
    </svg> 
);


export default function SortView({ type, column }) {

    let sortColumn = column;
    if (!sortColumn) {
        sortColumn = "Default";
    }

    const svg = {
        default: {
            icon: defaultSVG,
            span: "Default"
        },
        ascending: {
            icon: ascendingSVG,
            span: sortColumn
        },
        descending: {
            icon: descendingSVG,
            span: sortColumn
        }
    };

    return (
        <div id="sort-view-container" className="pointer">  
            <div id="sort-icon" >
                { svg[type]["icon"] }
            </div>

            <span className="pointer">{svg[type]["span"]}</span>
        </div>
    )

}
