import React from 'react';
import axios from 'axios';
import DateSquare from './DateSquare.js';

function DateSquares() {
    return (
        <div class="grid-container-large">
            <DateSquare />
            <DateSquare />
            <DateSquare />
        </div>
    )
}

export default class Calendar extends React.Component {
    state = {
        calendar: ''
    }

    componentDidMount() {
        var calendar_id = window.location.pathname.split("/")[5];  // this is bad and may break if URL changes
        axios.get('/fantasy-calendar/api/calendars/' + calendar_id)
            .then(res => {
                const calendar = res.data;
                this.setState({ calendar });
            })
    }

    render() {
        return (
            <div>
                <h4>Here is the calendar named {this.state.calendar.calendar_name}:</h4>
                <DateSquares />
            </div>
        )
    }
}