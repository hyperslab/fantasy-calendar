import React from 'react';
import CalendarPage from './CalendarPage.js';
import PageForwardButton from './PageForwardButton.js';
import PageBackButton from './PageBackButton.js';
import DisplayUnitSelect from './DisplayUnitSelect.js';
import DisplayUnitNameHeader from './DisplayUnitNameHeader.js';
import DisplayIterationSelect from './DisplayIterationSelect.js';
import BookmarkSelect from './BookmarkSelect.js';
import BookmarkCreateModalButton from './BookmarkCreateModalButton.js';
import NoteManageModalButton from './NoteManageModalButton.js';
import NoteViewModalButton from './NoteViewModalButton.js';
import DateFormatSearch from './DateFormatSearch.js';
import * as api from '../apiAccess.js';

export default function Calendar({ calendarId, displayConfigId = null, displayUnitId = null, displaySubUnitId = null, displayIteration = null }) {
    const [calendar, setCalendar] = React.useState('');
    const [timeUnits, setTimeUnits] = React.useState('');
    const [displayPage, setDisplayPage] = React.useState({ timeUnit: '', subUnit: '', iteration: '' });
    const [dateBookmarks, setDateBookmarks] = React.useState('');
    const [selectedBookmarkId, setSelectedBookmarkId] = React.useState('');  // set this back to empty string whenever it changes
    const [userStatus, setUserStatus] = React.useState('unauthenticated');  // 'unauthenticated', 'authenticated', or 'creator'
    const [displayConfig, setDisplayConfig] = React.useState('');

    const didMount = React.useRef(false);

    // initial setup
    React.useEffect(() => {
        // required props validation
        if (!calendarId) return;  // note: 0 is an invalid calendarId, failing there is intentional

        api.getUserStatusByCalendarId(calendarId, res => {
            setUserStatus(res.data.user_status);
        });
        api.getCalendarDetail(calendarId, resCalendar => {
            const calendar = resCalendar.data;
            setCalendar(calendar);
            setTimeUnits(calendar.time_units);
            displayConfigId = displayConfigId ?? calendar.default_display_config;
            if (displayConfigId)  // 0 can be passed explicitly to this.props.displayConfigId to force using no display config on calendars with a default set
            {
                api.getDisplayConfig(displayConfigId, resDisplayConfig => {
                    // save full display config to state
                    const displayConfig = resDisplayConfig.data;
                    setDisplayConfig(displayConfig);

                    // only show bookmarks with a matching time unit page
                    const allowedBookmarks = calendar.date_bookmarks.filter(dateBookmark => displayConfig.display_unit_configs.find(page => page.time_unit == dateBookmark.bookmark_unit && page.sub_unit == dateBookmark.bookmark_sub_unit));
                    setDateBookmarks(allowedBookmarks);

                    // determine initial time unit page with priority props > config default
                    var displayUnit = calendar.time_units.find(x => x.id == displayConfig.display_unit_configs.find(y => y.id == displayConfig.default_display_unit_config).time_unit);
                    var displaySubUnit = calendar.time_units.find(x => x.id == displayConfig.display_unit_configs.find(y => y.id == displayConfig.default_display_unit_config).sub_unit);
                    if (displayUnitId)
                    {
                        var matchingPage = null;
                        if (displaySubUnitId)
                        {
                            // must have a page matching time unit AND sub unit if sub unit is provided
                            matchingPage = displayConfig.display_unit_configs.find(x => x.time_unit == displayUnitId && x.sub_unit == displaySubUnitId);
                        }
                        else
                        {
                            // must page a page matching time unit with NO sub unit if sub unit is not provided
                            matchingPage = displayConfig.display_unit_configs.find(x => x.time_unit == displayUnitId && (!x.sub_unit || x.sub_unit == x.time_unit));
                        }
                        if (matchingPage)  // reassign to page specified by props if props are provided and the page exists
                        {
                            displayUnit = calendar.time_units.find(x => x.id == displayUnitId);
                            displaySubUnit = displaySubUnitId ? calendar.time_units.find(x => x.id == displaySubUnitId) : null;
                        }
                    }

                    // determine initial iteration with priority prop > default bookmark > 1
                    var initialIteration = 1;
                    if (displayIteration && typeof displayIteration === 'number' && displayIteration > 0)
                    {
                        initialIteration = displayIteration;
                    }
                    else if (displayConfig.default_date_bookmark)
                    {
                        const defaultDateBookmark = allowedBookmarks.find(x => x.id == displayConfig.default_date_bookmark);
                        if (defaultDateBookmark)
                        {
                            initialIteration = defaultDateBookmark.bookmark_iteration;
                        }
                    }

                    setDisplayPage({ timeUnit: displayUnit, subUnit: displaySubUnit ?? '', iteration: initialIteration });

                    api.loadBookmarks(calendar, displayConfigId);
                    api.loadAdjacent(displayUnit.id, displaySubUnit?.id, initialIteration, displayConfigId);
                });
            }
            else  // if there is no display config being used, checks for what is allowed are much less strict
            {
                // all pages are allowed, so all bookmarks are allowed
                setDateBookmarks(calendar.date_bookmarks);

                // determine initial time unit page with priority props > config default
                var displayUnit = calendar.time_units[0];
                var displaySubUnit = null;
                if (displayUnitId && calendar.time_units.find(x => x.id == displayUnitId))
                {
                    displayUnit = calendar.time_units.find(x => x.id == displayUnitId);

                    // must specify a time unit to specify a sub unit
                    if (displaySubUnitId  && calendar.time_units.find(x => x.id == displaySubUnitId))
                    {
                        displaySubUnit = calendar.time_units.find(x => x.id == displaySubUnitId);
                    }
                }

                // determine initial iteration with priority prop > 1
                var initialIteration = 1;
                if (displayIteration && typeof displayIteration === 'number' && displayIteration > 0)
                {
                    initialIteration = displayIteration;
                }

                setDisplayPage({ timeUnit: displayUnit, subUnit: displaySubUnit ?? '', iteration: initialIteration });

                api.loadBookmarks(calendar);
                api.loadAdjacent(displayUnit.id, displaySubUnit?.id, initialIteration);
            }
        });
    }, [calendarId, displayConfigId, displayUnitId, displaySubUnitId, displayIteration]);

    // pre-cache adjacent pages whenever the page changes
    React.useEffect(() => {
        // skip on first render
        if (!didMount.current) {
            didMount.current = true;
            return;
        }

        api.loadAdjacent(displayPage.timeUnit.id, displayPage.subUnit?.id, displayPage.iteration, displayConfig?.id);
    }, [displayPage, displayConfig]);

    function handlePageBackClick() {
        setDisplayPage(prevPage => ({
            ...prevPage,
            iteration: prevPage.iteration > 1 ? prevPage.iteration - 1 : prevPage.iteration,  // don't go below 1
        }));
    }

    function handlePageForwardClick () {
        setDisplayPage(prevPage => ({
            ...prevPage,
            iteration: prevPage.iteration + 1,
        }));
    }

    function handleTimeUnitInstanceClick(timeUnitId, subUnitId, iteration) {
        setDisplayPage({
            timeUnit: timeUnits.find(x => x.id == timeUnitId),
            subUnit: subUnitId ? timeUnits.find(x => x.id == subUnitId) : '',
            iteration: iteration,
        });
    }

    function handleDisplayUnitSelectChange(newUnitId, newSubUnitId) {
        api.getTimeUnitEquivalentIteration(displayPage.timeUnit.id, displayPage.iteration, newUnitId, res => {
            setDisplayPage({
                timeUnit: timeUnits.find(x => x.id == newUnitId),
                subUnit: timeUnits.find(x => x.id == newSubUnitId),
                iteration: res.data.iteration,
            });
        });
    }

    function handleDisplayIterationChange(newIteration) {
        if (!newIteration || newIteration < 1)
            newIteration = 1;
        else if (newIteration > Number.MAX_SAFE_INTEGER)
            newIteration = Number.MAX_SAFE_INTEGER;
        setDisplayPage({ ...displayPage, iteration: newIteration });
    }

    function handleBookmarkSelectChange(newBookmarkId) {
        const newBookmark = dateBookmarks.find(x => x.id == newBookmarkId);
        setDisplayPage({
            timeUnit: timeUnits.find(x => x.id == newBookmark.bookmark_unit),
            subUnit: newBookmark.bookmark_sub_unit != null ? timeUnits.find(x => x.id == newBookmark.bookmark_sub_unit) : '',
            iteration: newBookmark.bookmark_iteration,
        });
        setSelectedBookmarkId('');
    }

    function handleBookmarkCreateModalFormPostResponse(res) {
        setDateBookmarks(dateBookmarks => [...dateBookmarks, res.data]);
    }

    function handleNoteManageModalFormPostResponse(res) {
        return;  // TODO once we have an "all notes" section on the calendar itself update that
    }

    function handleDateFormatReverseGetResponse(res) {
        if ('time_unit_id' in res.data && 'iteration' in res.data) {
            setDisplayPage({
                ...displayPage,
                timeUnit: timeUnits.find(x => x.id == res.data.time_unit_id),
                iteration: res.data.iteration,
            });
        }
        else
            window.alert('Error parsing date format: ' + ('message' in res.data ? res.data.message : 'no message specified'));
    }

    // error message if required props missing
    if (!calendarId) return (
        <div className="calendar"><h2>COMPONENT ERROR: CALENDAR ID IS REQUIRED</h2></div>
    );

    // this just means it's still pulling data, not an error
    if (!calendar || !displayPage.timeUnit || !displayPage.iteration) return null;

    // helpers for calculation
    var displayUnitConfig;
    if (!displayPage.subUnit)
    {
        displayUnitConfig = displayConfig && displayConfig.display_unit_configs ? displayConfig.display_unit_configs.find(x => x.time_unit == displayPage.timeUnit.id) : null;
    }
    else
    {
        displayUnitConfig = displayConfig && displayConfig.display_unit_configs ? displayConfig.display_unit_configs.find(x => x.time_unit == displayPage.timeUnit.id && x.sub_unit == displayPage.subUnit.id) : null;
    }

    // parse display configurations and grab results to pass to components
    const timeUnitPages = displayConfig && displayConfig.display_unit_configs ? displayConfig.display_unit_configs.map(x => [timeUnits.find(y => y.id == x.time_unit), x.sub_unit !== null ? timeUnits.find(y => y.id == x.sub_unit) : null]) : timeUnits.map(x => [x, null]);
    const currentSearchType = displayUnitConfig ? displayUnitConfig.search_type : 'iteration';
    const searchableFormats = displayUnitConfig ? displayUnitConfig.searchable_date_formats : [];

    return (
        <div className="calendar">
            <h2>{calendar.calendar_name}</h2>
            <DisplayUnitNameHeader timeUnit={displayPage.timeUnit} iteration={displayPage.iteration} />
            <span className="calendar-top-controls">
                <PageBackButton timeUnitName={displayPage.timeUnit.time_unit_name} onClick={handlePageBackClick} />
                <span>
                    {timeUnitPages.length > 1 && <DisplayUnitSelect timeUnitPairs={timeUnitPages} currentUnitPair={[displayPage.timeUnit, displayPage.subUnit]} onChange={handleDisplayUnitSelectChange} />}
                    {timeUnitPages.length > 1 && ['iteration', 'formats'].includes(currentSearchType) && <>&nbsp;&nbsp;</>}
                    {currentSearchType == 'iteration' && <DisplayIterationSelect currentIteration={displayPage.iteration} onChange={handleDisplayIterationChange} />}
                    {currentSearchType == 'formats' && <DateFormatSearch searchableFormats={searchableFormats} handleGetResponse={handleDateFormatReverseGetResponse} />}
                </span>
                <span>
                    <BookmarkSelect bookmarks={dateBookmarks} selectedBookmarkId={selectedBookmarkId} onChange={handleBookmarkSelectChange} />
                    &nbsp;&nbsp;
                    <BookmarkCreateModalButton calendarId={calendarId} timeUnit={displayPage.timeUnit} subUnit={displayPage.subUnit} iteration={displayPage.iteration} userStatus={userStatus} handlePostResponse={handleBookmarkCreateModalFormPostResponse} />
                </span>
                <span>
                    <NoteManageModalButton calendarId={calendarId} timeUnit={displayPage.timeUnit} iteration={displayPage.iteration} userStatus={userStatus} handlePostResponse={handleNoteManageModalFormPostResponse} />
                    &nbsp;&nbsp;
                    <NoteViewModalButton timeUnit={displayPage.timeUnit} iteration={displayPage.iteration} />
                </span>
                <PageForwardButton timeUnitName={displayPage.timeUnit.time_unit_name} onClick={handlePageForwardClick} />
            </span>
            <CalendarPage timeUnit={displayPage.timeUnit} subUnit={displayPage.subUnit} iteration={displayPage.iteration} displayConfig={displayConfig} timeUnitInstanceClickHandler={handleTimeUnitInstanceClick} />
        </div>
    );
}