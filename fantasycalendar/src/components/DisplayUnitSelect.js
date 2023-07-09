import React from 'react';

export default function DisplayUnitSelect({ timeUnits, currentUnit, onChange }) {
    const options = [];

    timeUnits.forEach((timeUnit) => {
        options.push(
            <option key={timeUnit.id} value={timeUnit.id}>{timeUnit.time_unit_name}</option>
        );
    });

    return (
        <label>
            Time Unit:&nbsp;
            <select value={currentUnit.id} onChange={e => onChange(e.target.value)}>
                {options}
            </select>
        </label>
    );
}