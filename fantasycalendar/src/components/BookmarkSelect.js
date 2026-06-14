import React from 'react';

export default function BookmarkSelect({ bookmarks, selectedBookmarkId, onChange }) {
    const options = [];

    options.push(
        <option key={0} value="" disabled={true}>-Select to Navigate-</option>
    );

    if (bookmarks) {
        var personalBookmarks = bookmarks.filter(x => x.personal_bookmark_creator && !x.from_event);
        var sharedBookmarks = bookmarks.filter(x => !x.personal_bookmark_creator && !x.from_event);
        var eventBookmarks = bookmarks.filter(x => x.from_event);

        // show section labels if there is more than one section
        var showLabels = ((personalBookmarks && personalBookmarks.length > 0 ? 1 : 0)
                        + (sharedBookmarks && sharedBookmarks.length > 0 ? 1 : 0)
                        + (eventBookmarks && eventBookmarks.length > 0 ? 1 : 0)) > 1;

        if (personalBookmarks && personalBookmarks.length > 0) {
            if (showLabels) {
                options.push(
                    <option key={-1} value="" disabled={true}>--My Bookmarks--</option>
                );
            }
            personalBookmarks.forEach((bookmark) => {
                options.push(
                    <option key={bookmark.id} value={bookmark.id}>{bookmark.display_name}</option>
                );
            });
        }
        if (sharedBookmarks && sharedBookmarks.length > 0) {
            if (showLabels) {
                options.push(
                    <option key={-2} value="" disabled={true}>--Preset Bookmarks--</option>
                );
            }
            sharedBookmarks.forEach((bookmark) => {
                options.push(
                    <option key={bookmark.id} value={bookmark.id}>{bookmark.display_name}</option>
                );
            });
        }
        if (eventBookmarks && eventBookmarks.length > 0) {
            if (showLabels) {
                options.push(
                    <option key={-3} value="" disabled={true}>--Events--</option>
                );
            }
            eventBookmarks.forEach((bookmark) => {
                options.push(
                    <option key={bookmark.id} value={bookmark.id}>{bookmark.display_name}</option>
                );
            });
        }
    }

    return (
        <label>
            Bookmarks:&nbsp;
            <select value={selectedBookmarkId} onChange={e => onChange(e.target.value)}>
                {options}
            </select>
        </label>
    );
}