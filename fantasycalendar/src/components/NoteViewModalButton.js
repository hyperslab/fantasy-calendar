import React from 'react';
import Modal from 'react-modal';
import {getTimeUnitInstanceDisplayName, getUserNotes} from '../apiAccess.js';

const customStyles = {
    content: {
        background: 'lightgray',
        top: '15%',
        left: '40%',
        right: 'auto',
        bottom: 'auto',
        transform: 'translate(-30%)',
    },
    overlay: {
        backgroundColor: 'rgba(169, 169, 169, 0.75)',
    },
};

Modal.setAppElement('#root');

export default function NoteViewModalButton({ timeUnit, iteration }) {
    const [modalIsOpen, setModalIsOpen] = React.useState(false);
    const [notes, setNotes] = React.useState(null);
    const [displayName, setDisplayName] = React.useState('');

    function openModal() {
        setModalIsOpen(true);
        getTimeUnitInstanceDisplayName(timeUnit.id, iteration, res => {
            setDisplayName(res.data.display_name);
        });
        getUserNotes(timeUnit.id, iteration, res => {
            setNotes(res.data);
        });
    }

    function closeModal() {
        setModalIsOpen(false);
        setNotes(false);
    }

    const noteRows = [];
    if (notes && notes.length > 0) {
        let noteKey = 1;
        notes.forEach((note) => {
            noteRows.push(<li key={noteKey}>{note.note_creator_username}: {note.note_text}</li>);
            noteKey++;
        });
    }
    else {
        noteRows.push(<li key="0">No notes available for this date!</li>);
    }

    let modalContent;
    modalContent = <>
        <h3>All Notes</h3>
        <p>Notes for date: {displayName}</p>
        <ul>
            {noteRows}
        </ul>
    </>;

    return (
        <>
            <button onClick={openModal}>View Notes</button>
            <Modal style={customStyles} isOpen={modalIsOpen} onRequestClose={closeModal}>
                {modalContent}
            </Modal>
        </>
    );
}