import React from 'react';

export default function PageForwardButton({ timeUnitName, onClick }) {
    return (
        <button onClick={onClick}>
            Next {timeUnitName}
        </button>
    );
}