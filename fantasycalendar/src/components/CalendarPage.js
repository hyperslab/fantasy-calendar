import React from 'react';
import DateSquare from './DateSquare.js';
import LabelSquare from './LabelSquare.js';
import LabelRow from './LabelRow.js';
import {getCalendarPage} from '../apiAccess.js';
import LoadingIcon from "./LoadingIcon.js";

export default function CalendarPage({ timeUnit, subUnit, iteration, displayConfig, timeUnitInstanceClickHandler }) {
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

    let subUnitPage = calendarPage.sub_unit_page;
    if (subUnitPage && subUnitPage[0] == timeUnit.id && subUnitPage[1] == subUnit.id) {
        subUnitPage = null;  // don't allow navigation to the page we're already on
    }

    const squares = headerRow.concat(blankSquares.concat(calendarPage.calendar_dates.map(baseUnitInstance =>
        <DateSquare key={baseUnitInstance.iteration} timeUnitId={baseUnitInstance.time_unit_id} subUnitId={subUnitPage ? subUnitPage[1] : null} timeUnitInstance={baseUnitInstance} headerClickable={!!subUnitPage} timeUnitInstanceClickHandler={timeUnitInstanceClickHandler} showEventDescription={timeUnit.id==baseUnitInstance.time_unit_id} showExtraEventEllipsis={baseUnitInstance.not_all_events_returned} />
    )));

    // blocking
    const blockNames = [];
    const blockIterations = [];
    calendarPage.blocks.forEach((block) => {
        blockNames.push(block[0]);
        blockIterations.push(block[1]);
    });
    let blockUnitPage = calendarPage.block_unit_page;
    if (blockUnitPage && blockUnitPage[0] == timeUnit.id && blockUnitPage[1] == subUnit.id) {
        blockUnitPage = null;  // don't allow navigation to the page we're already on
    }
    if (blockNames.length > 0 && blockNames[0]) {
        let currentBlock = 0;
        while (currentBlock < blockNames.length) {
            let firstBlockInstance = calendarPage.calendar_dates.find(baseUnitInstance => baseUnitInstance.block_number > currentBlock);
            let firstBlockLocation = squares.findIndex(square => square.type === DateSquare && square.key == firstBlockInstance.iteration);
            if (currentBlock == 0) {
                firstBlockLocation -= calendarPage.initial_offset;
            }
            let firstBlockColumn = (firstBlockLocation - currentBlock) % calendarPage.row_length;
            const labelRowAndBlanks = [];
            if (calendarPage.row_length == 0 || currentBlock == 0 || firstBlockColumn == 0) {
                labelRowAndBlanks.push(<LabelRow key={-400-currentBlock} labelText={blockNames[currentBlock]} timeUnitId={blockUnitPage ? blockUnitPage[0] : null} subUnitId={blockUnitPage ? blockUnitPage[1] : null} timeUnitIteration={blockIterations[currentBlock]} headerClickable={!!blockUnitPage} timeUnitInstanceClickHandler={timeUnitInstanceClickHandler} />);
            }
            else {
                for (let i = 0; i < calendarPage.row_length - firstBlockColumn; i++) {
                    labelRowAndBlanks.push(<div key={-500-i-(currentBlock*1000)} />);
                }
                labelRowAndBlanks.push(<LabelRow key={-400-currentBlock} labelText={blockNames[currentBlock]} timeUnitId={blockUnitPage ? blockUnitPage[0] : null} subUnitId={blockUnitPage ? blockUnitPage[1] : null} timeUnitIteration={blockIterations[currentBlock]} headerClickable={!!blockUnitPage} timeUnitInstanceClickHandler={timeUnitInstanceClickHandler} />);
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
    const rowNames = [];
    const rowIterations = [];
    calendarPage.header_column.forEach((row) => {
        rowNames.push(row[0]);
        rowIterations.push(row[1]);
    });
    let rowUnitPage = calendarPage.row_unit_page;
    if (rowUnitPage && rowUnitPage[0] == timeUnit.id && rowUnitPage[1] == subUnit.id) {
        rowUnitPage = null;  // don't allow navigation to the page we're already on
    }
    if (calendarPage.row_length > 0 && rowNames.length > 0) {
        let currentBlock = 0;
        while (currentBlock < blockNames.length) {
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
                squares.splice(i, 0, <LabelSquare key={-200-rowNum-1} labelText={rowNames[Math.floor(rowNum)]} timeUnitId={rowUnitPage ? rowUnitPage[0] : null} subUnitId={rowUnitPage ? rowUnitPage[1] : null} timeUnitIteration={rowIterations[Math.floor(rowNum)]} headerClickable={!!rowUnitPage} timeUnitInstanceClickHandler={timeUnitInstanceClickHandler} />);
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