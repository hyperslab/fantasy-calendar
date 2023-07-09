import React from 'react';
import axios from 'axios';
import {getTimeUnitInstanceDisplayName} from '../apiAccess.js';

export default function DisplayUnitNameHeader({ timeUnit, iteration }) {
    const [displayName, setDisplayName] = React.useState('');

    React.useEffect(() => {
        getTimeUnitInstanceDisplayName(timeUnit.id, iteration, res => {
            setDisplayName(res.data.display_name);
        });
    }, [timeUnit, iteration]);

    return (
        <h4>
            {displayName}
        </h4>
    );
}