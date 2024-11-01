import { useState, useRef, useEffect, cloneElement } from "react";

import CarouselArrowSVG from "./CarouselArrowSVG";
import "./styles.css";


export default function MetaCarousel({ items }) {
    
    const [ index, setIndex ] = useState(0);
    const [ rightOn, setRightOn ] = useState(true);
    const [ leftOn, setLeftOn ] = useState(false);
    
    // Swipe Gestures
    const touchStartX = useRef(null);
    const touchStartY = useRef(null);
    
    const touchProps = {
        onTouchStart: handleTouchStart,
        onTouchMove: handleTouchMove,
        onTouchEnd: handleTouchEnd,
    }

    const carouselItems = items.map((item) => cloneElement(item, touchProps));
    

    useEffect(() => {
        
        const totalItems = items.length;

        setRightOn(index + 1 < totalItems);
        setLeftOn(index > 0);

    }, [index]);

    function getNewIndex(prevIndex, direction) {

        if (direction === "right") {
            return prevIndex + 1
        } else {
            return prevIndex - 1;
        }
    }

    function handleTouchStart(e) {

        touchStartX.current = e.touches[0].clientX;
        touchStartY.current = e.touches[0].clientY;
    }

    function handleTouchMove(e) {

        if (touchStartX === null) {
            return;
        }

        // Swipe Intention Options
        const minSwipeThreshold = 50;
        const maxVToHRatio = .5;

        const touchMoveX = e.touches[0].clientX;
        const touchMoveY = e.touches[0].clientY;
  
        const hSDistance = touchStartX.current - touchMoveX;
        const vDistance = touchStartY.current - touchMoveY;

        const vToHRatio = vDistance / hSDistance;
        
        // Determine if horizontal swipe was intended
        if (vToHRatio <= maxVToHRatio) {
            
            if (hSDistance < -minSwipeThreshold) {
                if (leftOn) {
                    setIndex((prevIndex) => getNewIndex(prevIndex, "left")); 
                }
            } 
            
            if (hSDistance > minSwipeThreshold) {
                if (rightOn) {
                    setIndex((prevIndex) => getNewIndex(prevIndex, "right"));
                }
            }
        }

    }

    function handleTouchEnd() {
        touchStartX.current = null;
        touchStartY.current = null;
    }

    function handleClick(isOn, direction) {
        
        if (!isOn) {
            return;
        }
    
        setIndex((prevIndex) => getNewIndex(prevIndex, direction));        
    }

    return (
        <div id="carousel-container" className="container">
            <CarouselArrowSVG 
                direction={ "left" } 
                isOn={ leftOn } 
                onClick={ handleClick }
            />
            { carouselItems[index] }
            <CarouselArrowSVG 
                direction={ "right" } 
                isOn={ rightOn } 
                onClick={ handleClick }
            />
        </div>
    )
}
