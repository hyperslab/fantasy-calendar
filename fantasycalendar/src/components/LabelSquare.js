import React from 'react';

export default function LabelSquare({ labelText }) {
    const gridStyleOverrides = {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'rgb(153, 196, 210)',
    };

    return (
        <div className="grid-item" style={gridStyleOverrides}>
            <div className="grid-item-label">&nbsp;&nbsp;{labelText}&nbsp;&nbsp;</div>
        </div>
    );
}