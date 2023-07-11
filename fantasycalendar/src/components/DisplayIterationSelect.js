import React from 'react';

export default function DisplayIterationSelect({ currentIteration, onChange }) {
    return (
        <label>
            Iteration:&nbsp;
            <input type="number" value={currentIteration} onChange={e => onChange(Number(e.target.value))} />
        </label>
    );
}