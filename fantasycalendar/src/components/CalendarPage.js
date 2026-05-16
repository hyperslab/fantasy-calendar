import React from 'react';
import DateSquare from './DateSquare.js';
import LabelSquare from './LabelSquare.js';
import LabelRow from './LabelRow.js';
import {getCalendarPage} from '../apiAccess.js';
import LoadingIcon from "./LoadingIcon.js";

export default function CalendarPage({ timeUnit, subUnit, iteration, displayConfig, baseUnitInstanceClickHandler }) {
    const [calendarPage, setCalendarPage] = React.useState(null);
    const [loading, setLoading] = React.useState(0);

    React.useEffect(() => {
        setLoading(n => n + 1);
        getCalendarPage(timeUnit.id, subUnit?.id, iteration, displayConfig?.id ?? 0, res => {
            setCalendarPage(res.data);
            setLoading(n => n - 1);
        });
        return () => {
            setCalendarPage(null);  // have to clear it here or the old squares don't go away
        }
    }, [timeUnit, subUnit, iteration, displayConfig]);

    if (!calendarPage || loading > 0) return (
        <div className="grid-container" style={{gridTemplateColumns: 'auto', justifyContent: 'center'}}>
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

    // blocking
    if (calendarPage.block_names && calendarPage.block_names.length > 0 && calendarPage.block_names[0]) {
        let currentBlock = 0;
        while (currentBlock < calendarPage.block_names.length) {
            let firstBlockInstance = calendarPage.calendar_dates.find(baseUnitInstance => baseUnitInstance.block_number > currentBlock);
            let firstBlockLocation = squares.findIndex(square => square.type === DateSquare && square.key == firstBlockInstance.iteration);
            if (currentBlock == 0) {
                firstBlockLocation -= calendarPage.initial_offset;
            }
            let firstBlockColumn = (firstBlockLocation - currentBlock) % calendarPage.row_length;
            const labelRowAndBlanks = [];
            if (calendarPage.row_length == 0 || currentBlock == 0 || firstBlockColumn == 0) {
                labelRowAndBlanks.push(<LabelRow key={-400-currentBlock} labelText={calendarPage.block_names[currentBlock]} />);
            }
            else {
                for (let i = 0; i < calendarPage.row_length - firstBlockColumn; i++) {
                    labelRowAndBlanks.push(<div key={-500-i-(currentBlock*1000)} />);
                }
                labelRowAndBlanks.push(<LabelRow key={-400-currentBlock} labelText={calendarPage.block_names[currentBlock]} />);
                for (let i = 0; i < firstBlockColumn; i++) {
                    labelRowAndBlanks.push(<div key={-600-i-(currentBlock*1000)} />);
                }
            }
            labelRowAndBlanks.reverse().forEach(rowOrBlank =>
                squares.splice(firstBlockLocation, 0, rowOrBlank)
            );
            currentBlock++;
        }
    }

    // header column
    if (calendarPage.row_length > 0 && calendarPage.header_column && calendarPage.header_column.length > 0) {
        let currentBlock = 0;
        while (currentBlock < calendarPage.block_names.length) {
            let firstBlockInstance = calendarPage.calendar_dates.find(baseUnitInstance => baseUnitInstance.block_number > currentBlock);
            let firstLabelLocation = squares.findIndex(square => square.type === DateSquare && square.key == firstBlockInstance.iteration);
            while (firstLabelLocation > 0 && squares[firstLabelLocation-1].type === 'div') {
                firstLabelLocation--;
            }
            let lastBlockInstance = calendarPage.calendar_dates.findLast(baseUnitInstance => baseUnitInstance.block_number == currentBlock + 1);
            let lastBlockLocation = squares.findIndex(square => square.type === DateSquare && square.key == lastBlockInstance.iteration);
            for (let i = firstLabelLocation; i <= lastBlockLocation; i += calendarPage.row_length+1) {
                let firstDateSquareInRowLocation = i;
                while (squares[firstDateSquareInRowLocation].type !== DateSquare) {
                    firstDateSquareInRowLocation++;
                }
                let dateNum = calendarPage.calendar_dates.findIndex(baseUnitInstance => baseUnitInstance.iteration == squares[firstDateSquareInRowLocation].key);
                let rowNum = (dateNum + calendarPage.initial_offset) / calendarPage.row_length;
                squares.splice(i, 0, <LabelSquare key={-200-rowNum-1} labelText={calendarPage.header_column[Math.floor(rowNum)]} />);
                lastBlockLocation++;
            }
            currentBlock++;
        }
    }

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
        <div className="grid-container" style={gridStyleOverrides}>
            {squares}
        </div>
    );
}