def html_tooltip(tooltip_text, display_text='?', container_type='span'):
    """
    Return tooltip_text as a tooltip that will show on hover over
    display_text, which will be placed in container_type.

    Requires some CSS like so:

    .tooltip {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted black;
    }

    .tooltip .tooltip-text {
        visibility: hidden;
        width: 160px;
        background-color: midnightblue;
        color: lightgray;
        text-align: center;
        padding: 5px 0;
        border-radius: 6px;
        position: absolute;
        z-index: 1;
    }

    .tooltip:hover .tooltip-text {
        visibility: visible;
    }
    """
    return '<' + container_type + ' class="tooltip">' + str(display_text) + '<span class="tooltip-text">' + \
           str(tooltip_text) + '</span></' + container_type + '>'
