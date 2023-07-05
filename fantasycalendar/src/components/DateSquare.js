import React from 'react';
import axios from 'axios';
import EventRow from './EventRow.js';

export default function DateSquare({ timeUnitInstance }) {
    const [displayName, setDisplayName] = React.useState('');
    const [events, setEvents] = React.useState([]);

    React.useEffect(() => {
        const timeUnitId = timeUnitInstance.time_unit_id;
        const iteration = timeUnitInstance.iteration;
        axios.get('/fantasy-calendar/api/events/?time_unit_id= ' + timeUnitId + '&iteration=' + iteration)
            .then(res => {
                setEvents(res.data);
            });
        setDisplayName(timeUnitInstance.name);
    }, []);

    const rows = [];

    events.forEach((event) => {
        rows.push(
            <EventRow event={event} />
        );
    });

    return (
        <div className="grid-item">
            <h5>{displayName}</h5>
            {rows}
        </div>
    );

}