import React from 'react';
import Modal from 'react-modal';
import {getTimeUnitInstanceDisplayName, postDateBookmark, postPersonalDateBookmark} from '../apiAccess.js';

const customStyles = {
    content: {
        background: 'lightgray',
        top: '30%',
        left: '50%',
        right: 'auto',
        bottom: 'auto',
        marginRight: '-50%',
        transform: 'translate(-50%, -50%)',
    },
    overlay: {
        backgroundColor: 'rgba(169, 169, 169, 0.75)',
    },
};

Modal.setAppElement('#root');

export default function BookmarkCreateModalButton({ calendarId, timeUnit, iteration, userStatus, handlePostResponse }) {
    const [modalIsOpen, setModalIsOpen] = React.useState(false);
    const [bookmarkName, setBookmarkName] = React.useState('');
    const [displayName, setDisplayName] = React.useState('');
    const [createShared, setCreateShared] = React.useState(false);

    function openModal() {
        setModalIsOpen(true);
        getTimeUnitInstanceDisplayName(timeUnit.id, iteration, res => {
            setDisplayName(res.data.display_name);
        });
    }

    function closeModal() {
        setModalIsOpen(false);
    }

    function handleSubmit(event) {
        event.preventDefault();
        console.log('create shared: ' + createShared);
        if (createShared)
            postDateBookmark(calendarId, bookmarkName, timeUnit.id, iteration, handlePostResponse);
        else
            postPersonalDateBookmark(calendarId, bookmarkName, timeUnit.id, iteration, handlePostResponse);
        closeModal();
    }

    let creatorOptions = <></>;
    if (userStatus == 'creator')
        creatorOptions = <>
            <br/><br/>
            <label>
                Make bookmark available to all users?&nbsp;
                <input type="checkbox" checked={createShared} onChange={(e) => setCreateShared(e.target.checked)} />
            </label>
        </>;

    let modalContent;
    if (userStatus == 'unauthenticated')
        modalContent = <h3>Log In to Save Bookmarks</h3>;
    else
        modalContent = <>
            <h3>Create New Bookmark</h3>
            <form onSubmit={handleSubmit}>
                <p>Bookmark for date: {displayName}</p>
                <label>
                    Provide a custom name (optional):&nbsp;
                    <input type="text" value={bookmarkName} onChange={(e) => setBookmarkName(e.target.value)} />
                </label>
                {creatorOptions}
                <br/><br/>
                <input type="submit" value="Save" />
            </form>
        </>;

    return (
        <>
            <button onClick={openModal}>Bookmark this Date</button>
            <Modal style={customStyles} isOpen={modalIsOpen} onRequestClose={closeModal}>
                {modalContent}
            </Modal>
        </>
    );
}