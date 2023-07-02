import React from 'react';
import axios from 'axios';

function EventRow({ event }) {
    return (
        <>
            <br/>{ event.event_name }
        </>
    )
}

export default class DateSquare extends React.Component {
    state = {
        displayName: '',
        events: []
    }

    componentDidMount() {
        axios.get('/fantasy-calendar/api/events/')
            .then(res => {
                const events = res.data;
                this.setState({ events });
            })
        const displayName = 'TestName';
        this.setState({ displayName });
    }

    render() {
        const rows = [];

        this.state.events.forEach((event) => {
            rows.push(
                <EventRow event={event} />
            );
        });

        return (
            <div class="grid-item">
                <h5>{this.state.displayName}</h5>
                {rows}
            </div>
        );
    }
}