import React from 'react';
import CalendarPage from './CalendarPage.js';
import PageForwardButton from './PageForwardButton.js';
import PageBackButton from './PageBackButton.js';
import DisplayUnitSelect from './DisplayUnitSelect.js';
import DisplayUnitNameHeader from './DisplayUnitNameHeader.js';
import DisplayIterationSelect from './DisplayIterationSelect.js';
import BookmarkSelect from './BookmarkSelect.js';
import BookmarkCreateModalButton from './BookmarkCreateModalButton.js';
import DateFormatSearch from './DateFormatSearch.js';
import * as api from '../apiAccess.js';

export default class Calendar extends React.Component {
    state = {
        calendar: '',
        timeUnits: '',
        displayUnit: '',
        displaySubUnit: '',
        displayIteration: '',
        dateBookmarks: '',
        selectedBookmarkId: '',  // set this back to empty string whenever it changes
        userStatus: 'unauthenticated',  // 'unauthenticated', 'authenticated', or 'creator'
        displayConfig: '',
    }

    componentDidMount() {
        const loadData = async(calendar, displayConfig) => {
            // start calling API in the background to cache some data
            // always call this last after the API calls that are actually needed
            const loadCalendarPage = async(timeUnit, subUnit, iteration, displayConfig = null) => {
                api.getCalendarPage(timeUnit.id, subUnit?.id, iteration, displayConfig?.id, res => {});
            };
            calendar.date_bookmarks.forEach((bookmark) => {  // for bookmarks
                loadCalendarPage(calendar.time_units.find(x => x.id == bookmark.bookmark_unit),
                bookmark.bookmark_sub_unit != null ? calendar.time_units.find(x => x.id == bookmark.bookmark_sub_unit) : null,
                bookmark.bookmark_iteration,
                displayConfig);
            });
        };

        // required props validation
        if (!this.props.hasOwnProperty('calendarId') || !(this.props.calendarId)) return;  // note: 0 is an invalid calendarId, failing there is intentional

        var calendar_id = this.props.calendarId;
        api.getUserStatusByCalendarId(calendar_id, res => {
            this.setState({ userStatus: res.data.user_status });
        });
        api.getCalendarDetail(calendar_id, resCalendar => {
            const calendar = resCalendar.data;
            this.setState({
                calendar: calendar,
                timeUnits: calendar.time_units,
            });
            var displayConfigId = this.props.displayConfigId ?? calendar.default_display_config;
            if (displayConfigId)  // 0 can be passed explicitly to this.props.displayConfigId to force using no display config on calendars with a default set
            {
                api.getDisplayConfig(displayConfigId, resDisplayConfig => {
                    // save full display config to state
                    const displayConfig = resDisplayConfig.data;
                    this.setState({ displayConfig: displayConfig });

                    // only show bookmarks with a matching time unit page
                    const allowedBookmarks = calendar.date_bookmarks.filter(dateBookmark => displayConfig.display_unit_configs.find(page => page.time_unit == dateBookmark.bookmark_unit && page.sub_unit == dateBookmark.bookmark_sub_unit));
                    this.setState({ dateBookmarks: allowedBookmarks });

                    // determine initial time unit page with priority props > config default
                    var displayUnit = calendar.time_units.find(x => x.id == displayConfig.display_unit_configs.find(y => y.id == displayConfig.default_display_unit_config).time_unit);
                    var displaySubUnit = calendar.time_units.find(x => x.id == displayConfig.display_unit_configs.find(y => y.id == displayConfig.default_display_unit_config).sub_unit);
                    if (this.props.hasOwnProperty('displayUnitId') && this.props.displayUnitId)
                    {
                        var matchingPage = null;
                        if (this.props.hasOwnProperty('displaySubUnitId') && this.props.displaySubUnitId)
                        {
                            // must have a page matching time unit AND sub unit if sub unit is provided
                            matchingPage = displayConfig.display_unit_configs.find(x => x.time_unit == this.props.displayUnitId && x.sub_unit == this.props.displaySubUnitId);
                        }
                        else
                        {
                            // must page a page matching time unit with NO sub unit if sub unit is not provided
                            matchingPage = displayConfig.display_unit_configs.find(x => x.time_unit == this.props.displayUnitId && (!x.sub_unit || x.sub_unit == x.time_unit));
                        }
                        if (matchingPage)  // reassign to page specified by props if props are provided and the page exists
                        {
                            displayUnit = calendar.time_units.find(x => x.id == this.props.displayUnitId);
                            displaySubUnit = (this.props.hasOwnProperty('displaySubUnitId') && this.props.displaySubUnitId) ? calendar.time_units.find(x => x.id == this.props.displaySubUnitId) : null;
                        }
                    }
                    this.setState({ displayUnit: displayUnit });
                    if (displaySubUnit)
                    {
                        this.setState({ displaySubUnit: displaySubUnit });
                    }

                    // determine initial iteration with priority prop > default bookmark > 1
                    if (this.props.hasOwnProperty('displayIteration') && this.props.displayIteration && typeof this.props.displayIteration === 'number' && this.props.displayIteration > 0)
                    {
                        this.setState({ displayIteration: this.props.displayIteration });
                    }
                    else if (displayConfig.default_date_bookmark)
                    {
                        const defaultDateBookmark = allowedBookmarks.find(x => x.id == displayConfig.default_date_bookmark);
                        if (defaultDateBookmark)
                        {
                            this.setState({ displayIteration: defaultDateBookmark.bookmark_iteration });
                        }
                    }
                    else
                    {
                        this.setState({ displayIteration: 1 });
                    }
                    loadData(calendar, displayConfig);
                });
            }
            else  // if there is no display config being used, checks for what is allowed are much less strict
            {
                // all pages are allowed, so all bookmarks are allowed
                this.setState({ dateBookmarks: calendar.date_bookmarks });

                // determine initial time unit page with priority props > config default
                if (this.props.hasOwnProperty('displayUnitId') && this.props.displayUnitId && calendar.time_units.find(x => x.id == this.props.displayUnitId))
                {
                    this.setState({ displayUnit: calendar.time_units.find(x => x.id == this.props.displayUnitId) });

                    // must specify a time unit to specify a sub unit
                    if (this.props.hasOwnProperty('displaySubUnitId') && this.props.displaySubUnitId  && calendar.time_units.find(x => x.id == this.props.displaySubUnitId))
                    {
                        this.setState({ displaySubUnit: calendar.time_units.find(x => x.id == this.props.displaySubUnitId) });
                    }
                }
                else
                {
                    this.setState({ displayUnit: calendar.time_units[0] });
                }

                // determine initial iteration with priority prop > 1
                if (this.props.hasOwnProperty('displayIteration') && this.props.displayIteration && typeof this.props.displayIteration === 'number' && this.props.displayIteration > 0)
                {
                    this.setState({ displayIteration: this.props.displayIteration });
                }
                else
                {
                    this.setState({ displayIteration: 1 });
                }
                loadData(calendar);
            }
        });
    }

    handlePageBackClick = () => {
        if (this.state.displayIteration > 1)  // don't go below 1
            this.setState({ displayIteration: this.state.displayIteration - 1 });
    }

    handlePageForwardClick = () => {
        this.setState({ displayIteration: this.state.displayIteration + 1 });
    }

    handleTimeUnitInstanceClick = (timeUnitId, subUnitId, iteration) => {
        this.setState({
            displayUnit: this.state.timeUnits.find(x => x.id == timeUnitId),
            displaySubUnit: subUnitId ? this.state.timeUnits.find(x => x.id == subUnitId) : '',
            displayIteration: iteration,
        });
    }

    handleDisplayUnitSelectChange = (newUnitId, newSubUnitId) => {
        api.getTimeUnitEquivalentIteration(this.state.displayUnit.id, this.state.displayIteration, newUnitId, res => {
            this.setState({
                displayUnit: this.state.timeUnits.find(x => x.id == newUnitId),
                displaySubUnit: this.state.timeUnits.find(x => x.id == newSubUnitId),
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
            displaySubUnit: newBookmark.bookmark_sub_unit != null ? this.state.timeUnits.find(x => x.id == newBookmark.bookmark_sub_unit) : '',
            displayIteration: newBookmark.bookmark_iteration,
            selectedBookmarkId: '',
        });
    }

    handleBookmarkCreateModalFormPostResponse = (res) => {
        this.setState({ dateBookmarks: [...this.state.dateBookmarks, res.data] });
    }

    handleDateFormatReverseGetResponse = (res) => {
        if ('time_unit_id' in res.data && 'iteration' in res.data)
            this.setState({
                displayUnit: this.state.timeUnits.find(x => x.id == res.data.time_unit_id),
                displayIteration: res.data.iteration,
            });
        else
            window.alert('Error parsing date format: ' + ('message' in res.data ? res.data.message : 'no message specified'));
    }

    render() {
        // error message if required props missing
        if (!this.props.hasOwnProperty('calendarId') || !(this.props.calendarId)) return (
            <div className="calendar"><h2>COMPONENT ERROR: CALENDAR ID IS REQUIRED</h2></div>
        );

        // this just means it's still pulling data, not an error
        if (!this.state.calendar || !this.state.displayUnit || !this.state.displayIteration) return null;

        // helpers for calculation
        var displayUnitConfig;
        if (!this.state.displaySubUnit)
        {
            displayUnitConfig = this.state.displayConfig && this.state.displayConfig.display_unit_configs ? this.state.displayConfig.display_unit_configs.find(x => x.time_unit == this.state.displayUnit.id) : null;
        }
        else
        {
            displayUnitConfig = this.state.displayConfig && this.state.displayConfig.display_unit_configs ? this.state.displayConfig.display_unit_configs.find(x => x.time_unit == this.state.displayUnit.id && x.sub_unit == this.state.displaySubUnit.id) : null;
        }

        // parse display configurations and grab results to pass to components
        const timeUnitPages = this.state.displayConfig && this.state.displayConfig.display_unit_configs ? this.state.displayConfig.display_unit_configs.map(x => [this.state.timeUnits.find(y => y.id == x.time_unit), x.sub_unit !== null ? this.state.timeUnits.find(y => y.id == x.sub_unit) : null]) : this.state.timeUnits.map(x => [x, null]);
        const currentSearchType = displayUnitConfig ? displayUnitConfig.search_type : 'iteration';
        const searchableFormats = displayUnitConfig ? displayUnitConfig.searchable_date_formats : [];

        return (
            <div className="calendar">
                <h2>{this.state.calendar.calendar_name}</h2>
                <DisplayUnitNameHeader timeUnit={this.state.displayUnit} iteration={this.state.displayIteration} />
                <span className="calendar-top-controls">
                    <PageBackButton timeUnitName={this.state.displayUnit.time_unit_name} onClick={this.handlePageBackClick} />
                    <span>
                        {timeUnitPages.length > 1 && <DisplayUnitSelect timeUnitPairs={timeUnitPages} currentUnitPair={[this.state.displayUnit, this.state.displaySubUnit]} onChange={this.handleDisplayUnitSelectChange} />}
                        {timeUnitPages.length > 1 && ['iteration', 'formats'].includes(currentSearchType) && <>&nbsp;&nbsp;</>}
                        {currentSearchType == 'iteration' && <DisplayIterationSelect currentIteration={this.state.displayIteration} onChange={this.handleDisplayIterationChange} />}
                        {currentSearchType == 'formats' && <DateFormatSearch searchableFormats={searchableFormats} handleGetResponse={this.handleDateFormatReverseGetResponse} />}
                    </span>
                    <span>
                        <BookmarkSelect bookmarks={this.state.dateBookmarks} selectedBookmarkId={this.state.selectedBookmarkId} onChange={this.handleBookmarkSelectChange} />
                        &nbsp;&nbsp;
                        <BookmarkCreateModalButton calendarId={this.state.displayUnit.calendar} timeUnit={this.state.displayUnit} subUnit={this.state.displaySubUnit} iteration={this.state.displayIteration} userStatus={this.state.userStatus} handlePostResponse={this.handleBookmarkCreateModalFormPostResponse} />
                    </span>
                    <PageForwardButton timeUnitName={this.state.displayUnit.time_unit_name} onClick={this.handlePageForwardClick} />
                </span>
                <CalendarPage timeUnit={this.state.displayUnit} subUnit={this.state.displaySubUnit} iteration={this.state.displayIteration} displayConfig={this.state.displayConfig} timeUnitInstanceClickHandler={this.handleTimeUnitInstanceClick} />
            </div>
        );
    }
}