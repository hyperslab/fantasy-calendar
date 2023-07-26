import axios from 'axios';

const baseUrl = '/fantasy-calendar/api/';

function getAuthenticated(url, then) {
    axios.get(baseUrl + url).then(res => then(res));  // turns out session cookies are sent automatically so no extra auth needed
}

export function getUserStatusByWorldId(worldId, then) {
    const url = 'userstatus/?world_id=' + worldId;
    getAuthenticated(url, then);
}

export function getUserStatusByCalendarId(calendarId, then) {
    const url = 'userstatus/?calendar_id=' + calendarId;
    getAuthenticated(url, then);
}

export function getCalendar(calendarId, then) {
    const url = 'calendars/' + calendarId + '/';
    getAuthenticated(url, then);
}

export function getTimeUnit(timeUnitId, then) {
    const url = 'timeunits/' + timeUnitId + '/';
    getAuthenticated(url, then);
}

export function getTimeUnitsByCalendarId(calendarId, then) {
    const url = 'timeunits/?calendar_id=' + calendarId;
    getAuthenticated(url, then);
}

export function getTimeUnitBaseInstances(timeUnitId, iteration, then) {
    const url = 'timeunitbaseinstances/?time_unit_id=' + timeUnitId + '&iteration=' + iteration;
    getAuthenticated(url, then);
}

export function getTimeUnitInstanceDisplayName(timeUnitId, iteration, then) {
    const url = 'timeunitinstancedisplayname/?time_unit_id=' + timeUnitId + '&iteration=' + iteration;
    getAuthenticated(url, then);
}

export function getTimeUnitEquivalentIteration(timeUnitId, iteration, newTimeUnitId, then) {
    const url = 'timeunitequivalentiteration/?time_unit_id=' + timeUnitId + '&iteration=' + iteration + '&new_time_unit_id=' + newTimeUnitId;
    getAuthenticated(url, then);
}

export function getTimeUnitContainedIteration(timeUnitId, iteration, containingTimeUnitId, then) {
    const url = 'timeunitcontainediteration/?time_unit_id=' + timeUnitId + '&iteration=' + iteration + '&containing_time_unit_id=' + containingTimeUnitId;
    getAuthenticated(url, then);
}

export function getDateFormatReverse(dateFormat, possibleFormats, then) {
    const url = 'dateformatreverse/?formatted_date=' + dateFormat + '&possible_formats=' + possibleFormats;
    getAuthenticated(url, then);
}

export function getDisplayConfig(displayConfigId, then) {
    const url = 'displayconfigs/' + displayConfigId + '/';
    getAuthenticated(url, then);
}

export function getDateBookmark(dateBookmarkId, then) {
    const url = 'datebookmarks/' + dateBookmarkId + '/';
    getAuthenticated(url, then);
}

export function getDateBookmarksByCalendarId(calendarId, then) {
    const url = 'datebookmarks/?calendar_id=' + calendarId;
    getAuthenticated(url, then);
}

function getCookie(name) {  // copied from https://docs.djangoproject.com/en/3.2/ref/csrf/#ajax
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function postAuthenticated(url, params, then) {
    const csrftoken = getCookie('csrftoken');

    const config = {
        headers: {
            'content-type': 'application/json',
            'X-CSRFToken': csrftoken,
        }
    };

    axios.post(baseUrl + url, params, config).then(res => then(res));
}

export function postDateBookmark(calendarId, dateBookmarkName, bookmarkUnitId, bookmarkIteration, then) {
    const url = 'datebookmarks/';
    const params = {
        calendar: calendarId,
        date_bookmark_name: dateBookmarkName,
        bookmark_unit: bookmarkUnitId,
        bookmark_iteration: bookmarkIteration,
    };
    postAuthenticated(url, params, then);
}

export function postPersonalDateBookmark(calendarId, dateBookmarkName, bookmarkUnitId, bookmarkIteration, then) {
    const url = 'datebookmarkcreatepersonal/';
    const params = {
        calendar: calendarId,
        date_bookmark_name: dateBookmarkName,
        bookmark_unit: bookmarkUnitId,
        bookmark_iteration: bookmarkIteration,
    };
    postAuthenticated(url, params, then);
}