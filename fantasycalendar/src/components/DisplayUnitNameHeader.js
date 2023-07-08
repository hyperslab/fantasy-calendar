import React from 'react';
import axios from 'axios';

export default function DisplayUnitNameHeader({ timeUnit, iteration }) {
    const [displayName, setDisplayName] = React.useState('');

    React.useEffect(() => {
        axios.get('/fantasy-calendar/api/timeunitinstancedisplayname/?time_unit_id=' + timeUnit.id + '&iteration=' + iteration)
            .then(res => {
                setDisplayName(res.data.display_name);
            });
    }, [timeUnit, iteration]);

    return (
        <h4>
            {displayName}
        </h4>
    );
}