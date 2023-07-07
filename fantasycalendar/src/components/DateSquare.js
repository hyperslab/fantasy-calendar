import React from 'react';
import axios from 'axios';
import EventRow from './EventRow.js';

export default function DateSquare({ timeUnitInstance, baseUnitInstanceClickHandler }) {
    const [displayName, setDisplayName] = React.useState('');
    const [events, setEvents] = React.useState([]);
    const [timeUnit, setTimeUnit] = React.useState(null);
    const [iteration, setIteration] = React.useState(1);

    React.useEffect(() => {
        const timeUnitId = timeUnitInstance.time_unit_id;
        axios.get('/fantasy-calendar/api/events/?time_unit_id= ' + timeUnitId + '&iteration=' + timeUnitInstance.iteration)
            .then(res => {
                setEvents(res.data);
            });
        setDisplayName(timeUnitInstance.name);
        setIteration(timeUnitInstance.iteration);
        axios.get('/fantasy-calendar/api/timeunits/' + timeUnitId)
            .then(res => {
                setTimeUnit(res.data);
            });
    }, []);

    const rows = [];

    events.forEach((event) => {
        rows.push(
            <EventRow key={event.id} event={event} />
        );
    });

    return (
        <div className="grid-item">
            <h5 onClick={() => baseUnitInstanceClickHandler(timeUnit, iteration)}>{displayName}</h5>
            {rows}
        </div>
    );

}