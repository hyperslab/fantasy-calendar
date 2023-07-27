import React from 'react';
import DateSquare from './DateSquare.js';
import LabelSquare from './LabelSquare.js';
import {getTimeUnit, getTimeUnitBaseInstances, getTimeUnitContainedIteration} from '../apiAccess.js';

export default function DateSquares({ timeUnit, iteration, timeUnitPages, rowGroupingUnit, rowGroupingLabelType, baseUnitInstanceClickHandler }) {
    const [baseUnit, setBaseUnit] = React.useState(null);
    const [baseUnitInstances, setBaseUnitInstances] = React.useState(null);
    const [rowBaseUnitInstances, setRowBaseUnitInstances] = React.useState(null);
    const [firstRowOffset, setFirstRowOffset] = React.useState(0);

    React.useEffect(() => {
        getTimeUnitBaseInstances(timeUnit.id, iteration, res => {
            setBaseUnitInstances(res.data);
            if (res.data && res.data.length > 0)
                getTimeUnit(res.data[0].time_unit_id, res2 => {
                    setBaseUnit(res2.data);
                    if (rowGroupingUnit)  // these extra calls cause a lot of slowdown for whatever reason
                    {
                        getTimeUnitBaseInstances(rowGroupingUnit.id, 1, res3 => {
                            setRowBaseUnitInstances(res3.data);
                        });
                        getTimeUnitContainedIteration(rowGroupingUnit.base_unit, res.data[0].iteration, rowGroupingUnit.id, res3 => {
                            setFirstRowOffset(res3.data.iteration - 1);
                        });
                    }
                });
        });
        return () => {
            setBaseUnitInstances(null);  // have to clear it here or the old squares don't go away
            setFirstRowOffset(0);
        }
    }, [timeUnit, iteration, rowGroupingUnit, rowGroupingLabelType]);

    if (!baseUnit || !baseUnitInstances) return null;

    let labels = [];
    if (rowBaseUnitInstances)
    {
        if (rowGroupingLabelType == 'names')
            labels = rowBaseUnitInstances.map(baseUnitInstance =>
                <LabelSquare key={-100-baseUnitInstance.iteration} labelText={baseUnitInstance.name} />
            );
        if (rowGroupingLabelType == 'numbers')
            labels = rowBaseUnitInstances.map(baseUnitInstance =>
                <LabelSquare key={-100-baseUnitInstance.iteration} labelText={baseUnitInstance.iteration} />
            );
    }
    const blankSquares = [];
    for (let i = 0; i < firstRowOffset; i++) {
        blankSquares.push(<div key={0-i} />);
    }
    const headerClickable = timeUnitPages.map(x => x.id).includes(timeUnit.id);
    const squares = labels.concat(blankSquares.concat(baseUnitInstances.map(baseUnitInstance =>
        <DateSquare key={baseUnitInstance.iteration} timeUnit={baseUnit} timeUnitInstance={baseUnitInstance} headerClickable={headerClickable} baseUnitInstanceClickHandler={baseUnitInstanceClickHandler} />
    )));
    if (rowGroupingUnit && rowBaseUnitInstances && rowGroupingLabelType == 'counts')
        for (let i = 0; i < squares.length; i += rowBaseUnitInstances.length+1)
            squares.splice(i, 0, <LabelSquare key={-100-((i/(rowBaseUnitInstances.length+1))+1)} labelText={rowGroupingUnit.time_unit_name + ' ' + ((i/(rowBaseUnitInstances.length+1))+1)} />);

    // CSS adjustments for row grouping and labels
    const gridStyleOverrides = {};
    if (rowBaseUnitInstances)
        gridStyleOverrides.gridTemplateColumns = (rowGroupingLabelType == 'counts' ? 'max-content ' : '') + 'repeat(' + rowBaseUnitInstances.length + ', auto)';
    if (rowGroupingUnit && rowBaseUnitInstances && (rowGroupingLabelType == 'names' || rowGroupingLabelType == 'numbers'))
        gridStyleOverrides.gridTemplateRows = 'auto';

    return (
        <div className="grid-container-large" style={gridStyleOverrides}>
            {squares}
        </div>
    );
}