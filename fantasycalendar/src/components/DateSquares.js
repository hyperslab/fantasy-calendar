import React from 'react';
import axios from 'axios';
import DateSquare from './DateSquare.js';
import {getTimeUnit, getTimeUnitBaseInstances} from '../apiAccess.js';

export default function DateSquares({ timeUnit, iteration, baseUnitInstanceClickHandler }) {
    const [baseUnit, setBaseUnit] = React.useState(null);
    const [baseUnitInstances, setBaseUnitInstances] = React.useState(null);

    React.useEffect(() => {
        getTimeUnitBaseInstances(timeUnit.id, iteration, res => {
            setBaseUnitInstances(res.data);
            if (res.data && res.data.length > 0)
                getTimeUnit(res.data[0].time_unit_id, res2 => {
                    setBaseUnit(res2.data);
                });
        });
        return () => {
            setBaseUnitInstances(null);  // have to clear it here or the old squares don't go away
        }
    }, [timeUnit, iteration]);

    if (!baseUnit || !baseUnitInstances) return null;

    const squares = baseUnitInstances.map(baseUnitInstance =>
        <DateSquare key={baseUnitInstance.iteration} timeUnit={baseUnit} timeUnitInstance={baseUnitInstance} baseUnitInstanceClickHandler={baseUnitInstanceClickHandler} />
    );

    return (
        <div className="grid-container-large">
            {squares}
        </div>
    );
}