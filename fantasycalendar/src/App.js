import React from 'react'

function DateSquare() {
    return (
        <div class="grid-item">
            date
        </div>
    )
}

function DateSquares() {
    return (
        <div class="grid-container">
            <DateSquare />
            <DateSquare />
            <DateSquare />
        </div>
    )
}

function App() {
    return (
        <div>
            <h4>Here is the calendar:</h4>
            <DateSquares />
        </div>
    )
}

export default App