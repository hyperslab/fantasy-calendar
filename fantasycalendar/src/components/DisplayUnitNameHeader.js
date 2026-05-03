import React from 'react';
import axios from 'axios';
import {getTimeUnitInstanceDisplayName} from '../apiAccess.js';

export default function DisplayUnitNameHeader({ timeUnit, iteration }) {
    const [displayName, setDisplayName] = React.useState('');
    const [instancePageLink, setInstancePageLink] = React.useState('');

    React.useEffect(() => {
        getTimeUnitInstanceDisplayName(timeUnit.id, iteration, res => {
            setDisplayName(res.data.display_name);
            setInstancePageLink(res.data.page_link);
        });
    }, [timeUnit, iteration]);

    return (
        <h4>
            {instancePageLink ? (instancePageLink && <a href={instancePageLink}>{displayName}</a>) : displayName}
        </h4>
    );
}