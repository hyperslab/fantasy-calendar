import React from 'react';
import axios from 'axios';
import DateSquares from './DateSquares.js';
import PageForwardButton from './PageForwardButton.js';
import PageBackButton from './PageBackButton.js';
import DisplayUnitSelect from './DisplayUnitSelect.js';
import DisplayUnitNameHeader from './DisplayUnitNameHeader.js';

export default class Calendar extends React.Component {
    state = {
        calendar: '',
        timeUnits: '',
        displayUnit: '',
        displayIteration: '',
        displayConfig: '',
        dateBookmark: ''
    }

    componentDidMount() {
        var calendar_id = window.location.pathname.split("/")[5];  // this is bad and may break if URL changes
        axios.get('/fantasy-calendar/api/calendars/' + calendar_id + '/')
            .then(res => {
                const calendar = res.data;
                this.setState({ calendar });
                axios.get('/fantasy-calendar/api/timeunits/?calendar_id=' + calendar_id)
                    .then(res => {
                        const timeUnits = res.data;
                        this.setState({ timeUnits });
                    });
                if (calendar.default_display_config)
                    axios.get('/fantasy-calendar/api/displayconfigs/' + calendar.default_display_config + '/')
                        .then(res2 => {
                            const displayConfig = res2.data;
                            this.setState({ displayConfig });
                            const displayUnitId = displayConfig.display_unit;
                            axios.get('/fantasy-calendar/api/timeunits/' + displayUnitId + '/')
                                .then(res3 => {
                                    const displayUnit = res3.data;
                                    this.setState({ displayUnit });
                                    if (displayConfig.default_date_bookmark)
                                        axios.get('/fantasy-calendar/api/datebookmarks/' + displayConfig.default_date_bookmark + '/')
                                            .then(res4 => {
                                                const dateBookmark = res4.data;
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
                        });
                else  // from if (calendar.default_display_config)
                    axios.get('/fantasy-calendar/api/timeunits/?calendar_id=' + calendar_id)
                        .then(res5 => {
                            const displayUnit = res5.data[0];
                            const displayIteration = 1;
                            this.setState({ displayUnit });
                            this.setState({ displayIteration });
                        });
            });
    }

    handlePageBackClick = () => {
        this.setState({ displayIteration: this.state.displayIteration - 1 });
    }

    handlePageForwardClick = () => {
        this.setState({ displayIteration: this.state.displayIteration + 1 });
    }

    handleBaseUnitInstanceClick = (baseUnit, baseIteration) => {
        this.setState({ displayUnit: baseUnit, displayIteration: baseIteration });
    }

    handleDisplayUnitSelectChange = (newUnitId) => {
        this.setState({ displayUnit: this.state.timeUnits.find(x => x.id == newUnitId) });
    }

    render() {
        if (!this.state.calendar || !this.state.displayUnit || !this.state.displayIteration) return null;
        return (
            <div className="calendar">
                <h2>{this.state.calendar.calendar_name}</h2>
                <DisplayUnitNameHeader timeUnit={this.state.displayUnit} iteration={this.state.displayIteration} />
                <span className="calendar-top-controls">
                    <PageBackButton timeUnitName={this.state.displayUnit.time_unit_name} onClick={this.handlePageBackClick} />
                    <DisplayUnitSelect timeUnits={this.state.timeUnits} currentUnit={this.state.displayUnit} onChange={this.handleDisplayUnitSelectChange} />
                    <PageForwardButton timeUnitName={this.state.displayUnit.time_unit_name} onClick={this.handlePageForwardClick} />
                </span>
                <DateSquares timeUnit={this.state.displayUnit} iteration={this.state.displayIteration} baseUnitInstanceClickHandler={this.handleBaseUnitInstanceClick} />
            </div>
        );
    }
}