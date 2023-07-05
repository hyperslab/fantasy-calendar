import React from 'react';
import axios from 'axios';

function EventRow({ event }) {
    return (
        <>
            <br/>{ event.event_name }
        </>
    );
}

export default class DateSquare extends React.Component {
    state = {
        displayName: '',
        events: []
    }

    componentDidMount() {
        const timeUnitId = this.props.timeUnitInstance.time_unit_id;
        const iteration = this.props.timeUnitInstance.iteration;
        axios.get('/fantasy-calendar/api/events/?time_unit_id= ' + timeUnitId + '&iteration=' + iteration)
            .then(res => {
                const events = res.data;
                this.setState({ events });
            });
        const displayName = this.props.timeUnitInstance.name;
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
            <div className="grid-item">
                <h5>{this.state.displayName}</h5>
                {rows}
            </div>
        );
    }
}