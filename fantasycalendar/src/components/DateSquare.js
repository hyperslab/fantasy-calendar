import React from 'react';
import EventRow from './EventRow.js';

export default function DateSquare({ timeUnitId, timeUnitInstance, headerClickable, baseUnitInstanceClickHandler, showEventDescription, maxEvents, showLinkedDisplayNames, showLinkedEvents }) {
    const rows = [];
    let header = timeUnitInstance.display_name;
    const displayEvents = [];

    timeUnitInstance.events.forEach((event) => {
        displayEvents.push(event);
    });

    if (showLinkedEvents)
    {
        timeUnitInstance.linked_events.forEach((event) => {
            displayEvents.push(event);
        });
    }

    displayEvents.slice(0, maxEvents).forEach((event) => {
        rows.push(
            <EventRow key={event.id} event={event} showDescription={showEventDescription} />
        );
    });

    if (showLinkedDisplayNames)
    {
        timeUnitInstance.linked_display_names.forEach((linked_display_name) => {
            header = header + ' - ' + linked_display_name;
        });
    }

    return (
        <div className="grid-item">
            {headerClickable ? (
                <h5 className="clickable-text" onClick={() => baseUnitInstanceClickHandler(timeUnitId, timeUnitInstance.iteration)}>{header}</h5>
            ) : (
                <h5>{header}</h5>
            )}
            {rows}
            {maxEvents != 0 && displayEvents.length > maxEvents && <div>...</div>}
        </div>
    );

}