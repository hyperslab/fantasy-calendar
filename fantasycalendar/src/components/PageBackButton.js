import React from 'react';

export default function PageBackButton({ timeUnitName, onClick }) {
    return (
        <button onClick={onClick}>
            Previous {timeUnitName}
        </button>
    );
}