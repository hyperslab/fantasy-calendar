import React from 'react';
import axios from 'axios';

export default function EventRow({ event }) {
    return (
        <>
            <br/>{ event.event_name }
        </>
    );
}