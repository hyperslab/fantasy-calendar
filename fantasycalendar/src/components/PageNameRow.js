import React from 'react';
import axios from 'axios';

export default function PageNameRow({ displayName, instancePageLink }) {
    const gridStyleOverrides = {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'rgb(153, 196, 210)',
        gridColumn: '1/-1',
        marginBottom: '3px'
    };

    return (
        <div className="grid-item" style={gridStyleOverrides}>
            <div className="grid-item-label-large">
                &nbsp;&nbsp;{instancePageLink ? (instancePageLink && <a href={instancePageLink}>{displayName}</a>) : displayName}&nbsp;&nbsp;
            </div>
        </div>
    );
}