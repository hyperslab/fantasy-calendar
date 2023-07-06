import React from 'react';
import axios from 'axios';
import DateSquare from './DateSquare.js';

export default function DateSquares({ timeUnitId, iteration }) {
    const [baseUnits, setBaseUnits] = React.useState(null);

    React.useEffect(() => {
        axios.get('/fantasy-calendar/api/timeunitbaseinstances/?time_unit_id=' + timeUnitId + '&iteration=' + iteration)
            .then(res => {
                setBaseUnits(res.data);
            });
    }, [iteration]);

    if (!baseUnits) return null;

    const squares = baseUnits.map(baseUnit =>
        <DateSquare key={baseUnit.iteration} timeUnitInstance={baseUnit} />
    );

    return (
        <div className="grid-container-large">
            {squares}
        </div>
    );
}