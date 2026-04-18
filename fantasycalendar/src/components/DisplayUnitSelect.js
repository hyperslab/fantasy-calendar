import React from 'react';

export default function DisplayUnitSelect({ timeUnitPairs, currentUnitPair, onChange }) {
    const options = [];

    timeUnitPairs.forEach(timeUnitPair => {
        var timeUnit = timeUnitPair[0];
        var subUnit = timeUnitPair[1];
        options.push(
            <option key={timeUnit.id + ',' + subUnit?.id} value={timeUnit.id + ',' + subUnit?.id}>{timeUnit.time_unit_name + (subUnit !== null ? ' by ' + subUnit.time_unit_name : '')}</option>
        );
    });

    return (
        <label>
            Time Unit:&nbsp;
            <select value={currentUnitPair[0].id + ',' + currentUnitPair[1]?.id} onChange={e => onChange(e.target.value.split(',')[0], e.target.value.split(',')[1])}>
                {options}
            </select>
        </label>
    );
}