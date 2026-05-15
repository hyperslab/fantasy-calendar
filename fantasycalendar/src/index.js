import React from "react";

import ReactDOM from "react-dom/client";

import App from "./App";

const root = ReactDOM.createRoot(document.getElementById("root"));
if (typeof calendarId === "undefined") {
    root.render("RENDERER ERROR: CALENDAR ID IS REQUIRED");
}
else {
    root.render(<App
                    calendarId={calendarId}
                    displayConfigId={typeof displayConfigId !== "undefined" ? displayConfigId : null}
                    displayUnitId={typeof displayUnitId !== "undefined" ? displayUnitId : null}
                    displaySubUnitId={typeof displaySubUnitId !== "undefined" ? displaySubUnitId : null}
                    displayIteration={typeof displayIteration !== "undefined" ? displayIteration : null}
                />);
}