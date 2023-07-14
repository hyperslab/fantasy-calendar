import axios from 'axios';

function getAuthenticated(url, then) {
    axios.get(url).then(res => then(res));  // turns out session cookies are sent automatically so no extra auth needed
}

export function getUserStatusByWorldId(worldId, then) {
    const url = '/fantasy-calendar/api/userstatus/?world_id=' + worldId;
    getAuthenticated(url, then);
}

export function getUserStatusByCalendarId(calendarId, then) {
    const url = '/fantasy-calendar/api/userstatus/?calendar_id=' + calendarId;
    getAuthenticated(url, then);
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

    axios.post(url, params, config).then(res => then(res));
}

export function postDateBookmark(calendarId, dateBookmarkName, bookmarkUnitId, bookmarkIteration, then) {
    const url = '/fantasy-calendar/api/datebookmarks/';
    const params = {
        calendar: calendarId,
        date_bookmark_name: dateBookmarkName,
        bookmark_unit: bookmarkUnitId,
        bookmark_iteration: bookmarkIteration,
    };
    postAuthenticated(url, params, then);
}

export function postPersonalDateBookmark(calendarId, dateBookmarkName, bookmarkUnitId, bookmarkIteration, then) {
    const url = '/fantasy-calendar/api/datebookmarkcreatepersonal/';
    const params = {
        calendar: calendarId,
        date_bookmark_name: dateBookmarkName,
        bookmark_unit: bookmarkUnitId,
        bookmark_iteration: bookmarkIteration,
    };
    postAuthenticated(url, params, then);
}