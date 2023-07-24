import React from 'react';
import {getDateFormatReverse} from '../apiAccess.js';

export default function DateFormatSearch({ searchableFormats, handleGetResponse }) {
    const [formattedDate, setFormattedDate] = React.useState('');

    function onSearchButtonClick() {
        getDateFormatReverse(formattedDate, searchableFormats, handleGetResponse);
    }

    return (
        <label>
            Date:&nbsp;
            <input type="text" value={formattedDate} onChange={e => setFormattedDate(e.target.value)} />
            &nbsp;
            <button onClick={onSearchButtonClick}>
                Search
            </button>
        </label>
    );
}