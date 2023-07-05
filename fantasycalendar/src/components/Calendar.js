import React from 'react';
import axios from 'axios';
import DateSquares from './DateSquares.js';

export default class Calendar extends React.Component {
    state = {
        calendar: '',
        displayUnit: '',
        displayIteration: '',
        displayConfig: '',
        dateBookmark: ''
    }

    componentDidMount() {
        var calendar_id = window.location.pathname.split("/")[5];  // this is bad and may break if URL changes
        axios.get('/fantasy-calendar/api/calendars/' + calendar_id)
            .then(res => {
                const calendar = res.data;
                this.setState({ calendar });
                if (calendar.default_display_config)
                    axios.get('/fantasy-calendar/api/displayconfigs/' + calendar.default_display_config)
                        .then(res2 => {
                            const displayConfig = res2.data;
                            const displayUnit = displayConfig.display_unit;
                            this.setState({ displayConfig });
                            this.setState({ displayUnit });
                            if (displayConfig.default_date_bookmark)
                                axios.get('/fantasy-calendar/api/datebookmarks/' + displayConfig.default_date_bookmark)
                                    .then(res3 => {
                                        const dateBookmark = res3.data;
                                        const displayIteration = dateBookmark.bookmark_iteration;
                                        this.setState({ dateBookmark });
                                        this.setState({ displayIteration });
                                    });
                            else  // from if (displayConfig.default_date_bookmark)
                            {
                                const displayIteration = 1;
                                this.setState({ displayIteration });
                            }
                        });
                else  // from if (calendar.default_display_config)
                    axios.get('/fantasy-calendar/api/timeunits/?calendar_id=' + calendar_id)
                        .then(res4 => {
                            const displayUnit = res4.data[0].id;
                            const displayIteration = 1;
                            this.setState({ displayUnit });
                            this.setState({ displayIteration });
                        });
            });
    }

    render() {
        if (!this.state.calendar || !this.state.displayUnit || !this.state.displayIteration) return null;
        return (
            <div>
                <h4>Here is the calendar named {this.state.calendar.calendar_name}:</h4>
                <DateSquares timeUnitId={this.state.displayUnit} iteration={this.state.displayIteration} />
            </div>
        );
    }
}