import React from 'react';

export default function EventRow({ event, showDescription }) {
    if (!showDescription || !event.event_description)
    {
        return (
            <div className="grid-item-row">
                { event.event_name }
            </div>
        );
    }
    else
    {
        return (
            <div className="grid-item-row-long">
                <b>{ event.event_name }:</b> { event.event_description }
            </div>
        );
    }
}