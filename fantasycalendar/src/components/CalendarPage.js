import React from 'react';
import DateSquare from './DateSquare.js';
import LabelSquare from './LabelSquare.js';
import {getCalendarPage} from '../apiAccess.js';
import LoadingIcon from "./LoadingIcon.js";

export default function CalendarPage({ timeUnit, iteration, displayConfig, baseUnitInstanceClickHandler }) {
    const [calendarPage, setCalendarPage] = React.useState(null);
    const [loading, setLoading] = React.useState(0);

    React.useEffect(() => {
        setLoading(n => n + 1);
        getCalendarPage(timeUnit.id, iteration, displayConfig?.id, res => {
            setCalendarPage(res.data);
            setLoading(n => n - 1);
        });
        return () => {
            setCalendarPage(null);  // have to clear it here or the old squares don't go away
        }
    }, [timeUnit, iteration, displayConfig]);

    if (!calendarPage || loading > 0) return (
        <div className="grid-container-large" style={{gridTemplateColumns: 'auto', justifyContent: 'center'}}>
            <LoadingIcon />
        </div>
    );

    let headerRow = [];
    if (calendarPage.header_row && calendarPage.header_row.length > 0)
    {
        headerRow = calendarPage.header_row.map((headerRowSquare, index) =>
            <LabelSquare key={-100-index} labelText={headerRowSquare} />
        );
    }

    const blankSquares = [];
    for (let i = 0; i < calendarPage.initial_offset; i++) {
        blankSquares.push(<div key={0-i} />);
    }

    const headerClickable = calendarPage.sub_unit_page_exists && calendarPage.calendar_dates[0].time_unit_id != timeUnit.id;

    const squares = headerRow.concat(blankSquares.concat(calendarPage.calendar_dates.map(baseUnitInstance =>
        <DateSquare key={baseUnitInstance.iteration} timeUnitId={baseUnitInstance.time_unit_id} timeUnitInstance={baseUnitInstance} headerClickable={headerClickable} baseUnitInstanceClickHandler={baseUnitInstanceClickHandler} showEventDescription={timeUnit.id==baseUnitInstance.time_unit_id} showExtraEventEllipsis={baseUnitInstance.not_all_events_returned} />
    )));

    if (calendarPage.row_length > 0 && calendarPage.header_column && calendarPage.header_column.length > 0)
        for (let i = headerRow.length; i < squares.length; i += calendarPage.row_length)
            squares.splice(i, 0, <LabelSquare key={-200-((i/(calendarPage.row_length))+1)} labelText={calendarPage.header_column[parseInt(i/(calendarPage.row_length))]} />);

    // CSS adjustments for bottom level time unit view and row grouping and labels
    const gridStyleOverrides = {};
    // grid-template-columns
    if (timeUnit.id == calendarPage.calendar_dates[0].time_unit_id)
        gridStyleOverrides.gridTemplateColumns = 'auto';
    else if ((calendarPage.header_row && calendarPage.header_row.length > 0) || (calendarPage.row_length > 0 && calendarPage.header_column && calendarPage.header_column.length > 0))
        gridStyleOverrides.gridTemplateColumns = (calendarPage.row_length > 0 && calendarPage.header_column && calendarPage.header_column.length > 0 ? 'max-content ' : '') + 'repeat(' + calendarPage.row_length + ', auto)';
    // grid-template-rows
    if (calendarPage.header_row && calendarPage.header_row.length > 0)
        gridStyleOverrides.gridTemplateRows = 'auto';

    return (
        <div className="grid-container-large" style={gridStyleOverrides}>
            {squares}
        </div>
    );
}