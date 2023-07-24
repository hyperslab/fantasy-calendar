import React from 'react';
import EventRow from './EventRow.js';

export default function DateSquare({ timeUnit, timeUnitInstance, headerClickable, baseUnitInstanceClickHandler }) {
    const rows = [];

    timeUnitInstance.events.forEach((event) => {
        rows.push(
            <EventRow key={event.id} event={event} />
        );
    });

    return (
        <div className="grid-item">
            {headerClickable ? (
                <h5 className="clickable-text" onClick={() => baseUnitInstanceClickHandler(timeUnit, timeUnitInstance.iteration)}>{timeUnitInstance.display_name}</h5>
            ) : (
                <h5>{timeUnitInstance.display_name}</h5>
            )}
            {rows}
        </div>
    );

}