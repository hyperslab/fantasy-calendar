import React from 'react';
import Modal from 'react-modal';
import {getTimeUnitInstanceDisplayName, postDateBookmark} from '../apiAccess.js';

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
};

Modal.setAppElement('#root');

export default function BookmarkCreateModalButton({ calendarId, timeUnit, iteration, handlePostResponse }) {
    const [modalIsOpen, setModalIsOpen] = React.useState(false);
    const [bookmarkName, setBookmarkName] = React.useState('');
    const [displayName, setDisplayName] = React.useState('');

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
        postDateBookmark(calendarId, bookmarkName, timeUnit.id, iteration, handlePostResponse);
        closeModal();
    }

    return (
        <>
            <button onClick={openModal}>Bookmark this Date</button>
            <Modal style={customStyles} isOpen={modalIsOpen} onRequestClose={closeModal}>
                <h3>Create New Bookmark</h3>
                <form onSubmit={handleSubmit}>
                    <p>Bookmark for date: {displayName}</p>
                    <label>
                        Provide a custom name (optional):&nbsp;
                        <input type="text" value={bookmarkName} onChange={(e) => setBookmarkName(e.target.value)} />
                    </label>
                    <br/><br/>
                    <input type="submit" value="Save" />
                </form>
            </Modal>
        </>
    );
}