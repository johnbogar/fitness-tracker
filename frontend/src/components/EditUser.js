import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

function EditUser(props) {
    const { user } = useAuth();

    const [firstname, setFirstname] = useState('');
    const [lastname, setLastname] = useState('');

    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        if (user) {
            const nameParts = user.name?.split(' ') || [];
            setFirstname(nameParts[0] || '');
            setLastname(nameParts[1] || '');
        }
    }, [user]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!firstname.trim() || !lastname.trim()) {
            setError('All fields are required');
            return;
        }

        try {
            const response = await fetch('http://localhost:5000/api/edit-user', {
                method: 'PUT',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    firstname,
                    lastname
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to update user');
            }

           setSuccess('Profile updated successfully!');
           setError('');
           setTimeout(() => {
                if (props.onUserUpdated) {
                    props.onUserUpdated();
                }
                props.onClose();
            }, 800);

        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal">

                {success && (
                    <>
                        <p className="success-message">{success}</p>
                        <button className="close-btn" onClick={props.onClose}>
                            Close
                        </button>
                    </>
                )}

                {!success && (
                    <form onSubmit={handleSubmit} className="edit-user-form">

                        <h2 className="form-title">Edit Profile</h2>

                        {error && <p className="error-message">{error}</p>}

                        <label className="form-label">First Name</label>
                        <input
                            className="form-input"
                            value={firstname}
                            onChange={(e) => setFirstname(e.target.value)}
                        />

                        <label className="form-label">Last Name</label>
                        <input
                            className="form-input"
                            value={lastname}
                            onChange={(e) => setLastname(e.target.value)}
                        />

                        <div className="form-buttons">
                            <button type="submit" className="submit-btn">
                                Update
                            </button>

                            <button
                                type="button"
                                className="close-btn"
                                onClick={props.onClose}
                            >
                                Close
                            </button>
                        </div>

                    </form>
                )}

            </div>
        </div>
    );
}

export default EditUser;