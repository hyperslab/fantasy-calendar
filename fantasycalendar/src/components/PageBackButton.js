import React from 'react';
import axios from 'axios';

export default function PageBackButton({ timeUnitName, onClick }) {
    return (
        <button onClick={onClick}>
            Previous {timeUnitName}
        </button>
    );
}