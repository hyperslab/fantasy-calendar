import React from 'react';

export default function LabelSquare({ labelText, timeUnitId, subUnitId, timeUnitIteration, headerClickable, timeUnitInstanceClickHandler }) {
    const gridStyleOverrides = {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'rgb(153, 196, 210)',
    };

    return (
        <div className="grid-item" style={gridStyleOverrides}>
            {headerClickable ? (
                <div className="grid-item-label clickable-text" onClick={() => timeUnitInstanceClickHandler(timeUnitId, subUnitId, timeUnitIteration)}>&nbsp;&nbsp;{labelText}&nbsp;&nbsp;</div>
            ) : (
                <div className="grid-item-label">&nbsp;&nbsp;{labelText}&nbsp;&nbsp;</div>
            )}
        </div>
    );
}