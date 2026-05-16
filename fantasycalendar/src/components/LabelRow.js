import React from 'react';

export default function LabelRow({ labelText, timeUnitId, subUnitId, timeUnitIteration, headerClickable, timeUnitInstanceClickHandler }) {
    const gridStyleOverrides = {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'rgb(153, 196, 210)',
        gridColumn: '1/-1'
    };

    return (
        <div className="grid-item" style={gridStyleOverrides}>
            {headerClickable ? (
                <div className="grid-item-label-large clickable-text" onClick={() => timeUnitInstanceClickHandler(timeUnitId, subUnitId, timeUnitIteration)}>&nbsp;&nbsp;{labelText}&nbsp;&nbsp;</div>
            ) : (
                <div className="grid-item-label-large">&nbsp;&nbsp;{labelText}&nbsp;&nbsp;</div>
            )}
        </div>
    );
}