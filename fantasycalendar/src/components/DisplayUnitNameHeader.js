import React from 'react';
import axios from 'axios';
import {getTimeUnitInstanceDisplayName} from '../apiAccess.js';

export default function DisplayUnitNameHeader({ displayName, instancePageLink }) {
    return (
        <h4>
            {instancePageLink ? (instancePageLink && <a href={instancePageLink}>{displayName}</a>) : displayName}
        </h4>
    );
}