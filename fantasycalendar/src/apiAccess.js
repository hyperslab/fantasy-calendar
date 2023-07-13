import axios from 'axios';

function getAuthenticated(url, then) {
    axios.get(url).then(res => then(res));  // turns out session cookies are sent automatically so no extra auth needed
}

export function getCalendar(calendarId, then) {
    const url = '/fantasy-calendar/api/calendars/' + calendarId + '/';
    getAuthenticated(url, then);
}

export function getTimeUnit(timeUnitId, then) {
    const url = '/fantasy-calendar/api/timeunits/' + timeUnitId + '/';
    getAuthenticated(url, then);
}

export function getTimeUnitsByCalendarId(calendarId, then) {
    const url = '/fantasy-calendar/api/timeunits/?calendar_id=' + calendarId;
    getAuthenticated(url, then);
}

export function getTimeUnitBaseInstances(timeUnitId, iteration, then) {
    const url = '/fantasy-calendar/api/timeunitbaseinstances/?time_unit_id=' + timeUnitId + '&iteration=' + iteration;
    getAuthenticated(url, then);
}

export function getTimeUnitEquivalentIteration(timeUnitId, iteration, newTimeUnitId, then) {
    const url = '/fantasy-calendar/api/timeunitequivalentiteration/?time_unit_id=' + timeUnitId + '&iteration=' + iteration + '&new_time_unit_id=' + newTimeUnitId;
    getAuthenticated(url, then);
}

export function getTimeUnitInstanceDisplayName(timeUnitId, iteration, then) {
    const url = '/fantasy-calendar/api/timeunitinstancedisplayname/?time_unit_id=' + timeUnitId + '&iteration=' + iteration;
    getAuthenticated(url, then);
}

export function getDisplayConfig(displayConfigId, then) {
    const url = '/fantasy-calendar/api/displayconfigs/' + displayConfigId + '/';
    getAuthenticated(url, then);
}

export function getDateBookmark(dateBookmarkId, then) {
    const url = '/fantasy-calendar/api/datebookmarks/' + dateBookmarkId + '/';
    getAuthenticated(url, then);
}

export function getDateBookmarksByCalendarId(calendarId, then) {
    const url = '/fantasy-calendar/api/datebookmarks/?calendar_id=' + calendarId;
    getAuthenticated(url, then);
}