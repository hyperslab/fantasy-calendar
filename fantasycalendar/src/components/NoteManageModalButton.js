import React from 'react';
import Modal from 'react-modal';
import {getTimeUnitInstanceDisplayName, getUserNote, postUserNote} from '../apiAccess.js';

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

export default function NoteManageModalButton({ calendarId, timeUnit, iteration, userStatus, handlePostResponse }) {
    const [modalIsOpen, setModalIsOpen] = React.useState(false);
    const [noteText, setNoteText] = React.useState('');
    const [displayName, setDisplayName] = React.useState('');
    const [editable, setEditable] = React.useState(false);

    function openModal() {
        setModalIsOpen(true);
        getTimeUnitInstanceDisplayName(timeUnit.id, iteration, res => {
            setDisplayName(res.data.display_name);
        });
        getUserNote(timeUnit.id, iteration, res => {
            if (res.data.length > 0) {
                setNoteText(res.data[0].note_text);
            }
            else {
                setNoteText('');
            }
            setEditable(true);
        });
    }

    function closeModal() {
        setModalIsOpen(false);
        setNoteText('');
        setEditable(false);
    }

    function handleSubmit(event) {
        event.preventDefault();
        postUserNote(calendarId, timeUnit.id, iteration, noteText, () => {
            closeModal();  // wait until post completes to reset fields to be sure they make it to the API
            handlePostResponse();
        });
    }

    let modalContent;
    if (userStatus == 'unauthenticated')
        modalContent = <h3>Log In to Save Notes</h3>;
    else
        modalContent = <>
            <h3>Personal Notes</h3>
            <form onSubmit={handleSubmit}>
                <p>Notes for date: {displayName}</p>
                <textarea rows="12" cols="60" disabled={!editable} value={noteText} onChange={(e) => setNoteText(e.target.value)} />
                <br/><br/>
                <input type="submit" value="Save" />
            </form>
        </>;

    return (
        <>
            <button onClick={openModal}>Save Notes</button>
            <Modal style={customStyles} isOpen={modalIsOpen} onRequestClose={closeModal}>
                {modalContent}
            </Modal>
        </>
    );
}