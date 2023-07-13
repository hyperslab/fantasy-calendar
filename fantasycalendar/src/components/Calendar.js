import React from 'react';
import axios from 'axios';
import DateSquares from './DateSquares.js';
import PageForwardButton from './PageForwardButton.js';
import PageBackButton from './PageBackButton.js';
import DisplayUnitSelect from './DisplayUnitSelect.js';
import DisplayUnitNameHeader from './DisplayUnitNameHeader.js';
import DisplayIterationSelect from './DisplayIterationSelect.js';
import BookmarkSelect from './BookmarkSelect.js';
import BookmarkCreateModalButton from './BookmarkCreateModalButton.js';
import * as api from '../apiAccess.js';

export default class Calendar extends React.Component {
    state = {
        calendar: '',
        timeUnits: '',
        displayUnit: '',
        displayIteration: '',
        dateBookmarks: '',
        selectedBookmarkId: '',  // set this back to empty string whenever it changes
        userStatus: 'unauthenticated',  // 'unauthenticated', 'authenticated', or 'creator'
    }

    componentDidMount() {
        var calendar_id = window.location.pathname.split("/")[5];  // this is bad and may break if URL changes
        api.getUserStatusByCalendarId(calendar_id, res => {
            this.setState({ userStatus: res.data.user_status });
        });
        api.getCalendar(calendar_id, res => {
            const calendar = res.data;
            this.setState({ calendar });
            api.getTimeUnitsByCalendarId(calendar_id, res6 => {
                const timeUnits = res6.data;
                this.setState({ timeUnits });
            });
            api.getDateBookmarksByCalendarId(calendar_id, res7 => {
                const dateBookmarks = res7.data;
                this.setState({ dateBookmarks });
            });
            if (calendar.default_display_config)
                api.getDisplayConfig(calendar.default_display_config, res2 => {
                    const displayConfig = res2.data;
                    const displayUnitId = displayConfig.display_unit;
                    api.getTimeUnit(displayUnitId, res3 => {
                        const displayUnit = res3.data;
                        this.setState({ displayUnit });
                        if (displayConfig.default_date_bookmark)
                            api.getDateBookmark(displayConfig.default_date_bookmark, res4 => {
                                const dateBookmark = res4.data;
                                const displayIteration = dateBookmark.bookmark_iteration;
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
                api.getTimeUnitsByCalendarId(calendar_id, res5 => {
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
        api.getTimeUnitEquivalentIteration(this.state.displayUnit.id, this.state.displayIteration, newUnitId, res => {
            this.setState({
                displayUnit: this.state.timeUnits.find(x => x.id == newUnitId),
                displayIteration: res.data.iteration,
            });
        });
    }

    handleDisplayIterationChange = (newIteration) => {
        if (!newIteration || newIteration < 1)
            newIteration = 1;
        else if (newIteration > Number.MAX_SAFE_INTEGER)
            newIteration = Number.MAX_SAFE_INTEGER;
        this.setState({ displayIteration: newIteration });
    }

    handleBookmarkSelectChange = (newBookmarkId) => {
        const newBookmark = this.state.dateBookmarks.find(x => x.id == newBookmarkId);
        this.setState({
            displayUnit: this.state.timeUnits.find(x => x.id == newBookmark.bookmark_unit),
            displayIteration: newBookmark.bookmark_iteration,
            selectedBookmarkId: '',
        });
    }

    handleBookmarkCreateModalFormPostResponse = (res) => {
        this.setState({ dateBookmarks: [...this.state.dateBookmarks, res.data] });
    }

    render() {
        if (!this.state.calendar || !this.state.displayUnit || !this.state.displayIteration) return null;

        let bookmarkButton = <></>;  // only show bookmark button for creators
        if (this.state.userStatus == 'creator')
            bookmarkButton = <>&nbsp;&nbsp;<BookmarkCreateModalButton calendarId={this.state.displayUnit.calendar} timeUnit={this.state.displayUnit} iteration={this.state.displayIteration} handlePostResponse={this.handleBookmarkCreateModalFormPostResponse} /></>

        return (
            <div className="calendar">
                <h2>{this.state.calendar.calendar_name}</h2>
                <DisplayUnitNameHeader timeUnit={this.state.displayUnit} iteration={this.state.displayIteration} />
                <span className="calendar-top-controls">
                    <PageBackButton timeUnitName={this.state.displayUnit.time_unit_name} onClick={this.handlePageBackClick} />
                    <span>
                        <DisplayUnitSelect timeUnits={this.state.timeUnits} currentUnit={this.state.displayUnit} onChange={this.handleDisplayUnitSelectChange} />
                        &nbsp;&nbsp;
                        <DisplayIterationSelect currentIteration={this.state.displayIteration} onChange={this.handleDisplayIterationChange} />
                    </span>
                    <span>
                        <BookmarkSelect bookmarks={this.state.dateBookmarks} selectedBookmarkId={this.state.selectedBookmarkId} onChange={this.handleBookmarkSelectChange} />
                        {bookmarkButton}
                    </span>
                    <PageForwardButton timeUnitName={this.state.displayUnit.time_unit_name} onClick={this.handlePageForwardClick} />
                </span>
                <DateSquares timeUnit={this.state.displayUnit} iteration={this.state.displayIteration} baseUnitInstanceClickHandler={this.handleBaseUnitInstanceClick} />
            </div>
        );
    }
}