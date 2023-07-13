import React from 'react';

export default function BookmarkSelect({ bookmarks, selectedBookmarkId, onChange }) {
    const options = [];

    options.push(
        <option key={0} value="">-Select to Navigate-</option>
    );

    bookmarks.forEach((bookmark) => {
        options.push(
            <option key={bookmark.id} value={bookmark.id}>{bookmark.display_name}</option>
        );
    });

    return (
        <label>
            Bookmarks:&nbsp;
            <select value={selectedBookmarkId} onChange={e => onChange(e.target.value)}>
                {options}
            </select>
        </label>
    );
}