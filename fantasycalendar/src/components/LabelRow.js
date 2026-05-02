import React from 'react';

export default function LabelRow({ labelText }) {
    const gridStyleOverrides = {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'rgb(153, 196, 210)',
        gridColumn: '1/-1'
    };

    return (
        <div className="grid-item" style={gridStyleOverrides}>
            <h3>&nbsp;&nbsp;{labelText}&nbsp;&nbsp;</h3>
        </div>
    );
}