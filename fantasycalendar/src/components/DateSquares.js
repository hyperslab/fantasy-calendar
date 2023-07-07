import React from 'react';
import axios from 'axios';
import DateSquare from './DateSquare.js';

export default function DateSquares({ timeUnit, iteration, baseUnitInstanceClickHandler }) {
    const [baseUnits, setBaseUnits] = React.useState(null);

    React.useEffect(() => {
        axios.get('/fantasy-calendar/api/timeunitbaseinstances/?time_unit_id=' + timeUnit.id + '&iteration=' + iteration)
            .then(res => {
                setBaseUnits(res.data);
            });
        return () => {
            setBaseUnits(null);  // have to clear it here or the old squares don't go away
        }
    }, [timeUnit, iteration]);

    if (!baseUnits) return null;

    const squares = baseUnits.map(baseUnit =>
        <DateSquare key={baseUnit.iteration} timeUnit={timeUnit} timeUnitInstance={baseUnit} baseUnitInstanceClickHandler={baseUnitInstanceClickHandler} />
    );

    return (
        <div className="grid-container-large">
            {squares}
        </div>
    );
}