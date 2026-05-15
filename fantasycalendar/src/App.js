import React from 'react';
import Calendar from './components/Calendar.js';

function App({ calendarId, displayConfigId, displayUnitId, displaySubUnitId, displayIteration }) {
    return (
        <div>
            <Calendar calendarId={calendarId} displayConfigId={displayConfigId} displayUnitId={displayUnitId} displaySubUnitId={displaySubUnitId} displayIteration={displayIteration} />
        </div>
    )
}

export default App