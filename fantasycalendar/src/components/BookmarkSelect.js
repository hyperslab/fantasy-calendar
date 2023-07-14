import React from 'react';

export default function BookmarkSelect({ bookmarks, selectedBookmarkId, onChange }) {
    const options = [];

    options.push(
        <option key={0} value="" disabled={true}>-Select to Navigate-</option>
    );

    if (bookmarks) {
        var personalBookmarks = bookmarks.filter(x => x.personal_bookmark_creator);
        var sharedBookmarks = bookmarks.filter(x => !x.personal_bookmark_creator);
        if (personalBookmarks && personalBookmarks.length > 0) {
            if (sharedBookmarks && sharedBookmarks.length > 0) {
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
            if (personalBookmarks && personalBookmarks.length > 0) {
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