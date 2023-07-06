import React from 'react';
import axios from 'axios';

export default function PageForwardButton({ timeUnitName, onClick }) {
    return (
        <button onClick={onClick}>
            Next {timeUnitName}
        </button>
    );
}