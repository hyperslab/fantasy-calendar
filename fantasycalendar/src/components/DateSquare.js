import React from 'react';
import axios from 'axios';
import EventRow from './EventRow.js';

export default function DateSquare({ timeUnit, timeUnitInstance, baseUnitInstanceClickHandler }) {
    const rows = [];

    timeUnitInstance.events.forEach((event) => {
        rows.push(
            <EventRow key={event.id} event={event} />
        );
    });

    return (
        <div className="grid-item">
            <h5 onClick={() => baseUnitInstanceClickHandler(timeUnit, timeUnitInstance.iteration)}>{timeUnitInstance.name}</h5>
            {rows}
        </div>
    );

}