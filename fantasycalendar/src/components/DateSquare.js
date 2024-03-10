import React from 'react';
import EventRow from './EventRow.js';

export default function DateSquare({ timeUnitId, timeUnitInstance, headerClickable, baseUnitInstanceClickHandler, showEventDescription }) {
    const rows = [];

    timeUnitInstance.events.forEach((event) => {
        rows.push(
            <EventRow key={event.id} event={event} showDescription={showEventDescription} />
        );
    });

    return (
        <div className="grid-item">
            {headerClickable ? (
                <h5 className="clickable-text" onClick={() => baseUnitInstanceClickHandler(timeUnitId, timeUnitInstance.iteration)}>{timeUnitInstance.display_name}</h5>
            ) : (
                <h5>{timeUnitInstance.display_name}</h5>
            )}
            {rows}
        </div>
    );

}